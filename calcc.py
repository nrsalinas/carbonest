import pandas as pd
import sqlalchemy as al
import numpy as np
import pyproj
import allometry
import wood_density as wd


user = ''
password = ''
database = ''

# Archivos (o carpetas) neesarios para los computos
densities_file = '/home/nelson/Documents/IDEAM/GlobalWoodDensityDB/gwddb_20180104.csv'

elevation_rasters = ('/home/nelson/Documents/GIS/Elevation/alt_30s_bil/alt.bil',)
#elevation_rasters = ('/home/nelsonsalinas/Documents/WorldClim/v1/alt/alt_23.tif', '/home/nelsonsalinas/Documents/WorldClim/v1/alt/alt_33.tif')
precipitation_raster_folder = '/home/nelson/Documents/IDEAM/WorldClim_v2/precipitation'
#precipitation_raster_folder = '/home/nelsonsalinas/Documents/WorldClim/v2/precipitation_30_sec'
chave_E_raster = '/home/nelson/Documents/IDEAM/Chave_E/E.bil'

engine = al.create_engine('mysql+mysqldb://{0}:{1}@localhost/{2}?charset=utf8&use_unicode=1&unix_socket=/var/run/mysqld/mysqld.sock'.format(user, password, database))
#engine = al.create_engine('mysql+mysqldb://{0}:{1}@localhost/{2}?charset=utf8&use_unicode=1'.format(user, password, database))

conn = engine.connect()

par = pd.read_sql_table(table_name='Parcelas', con = conn, index_col='PlotID')

# WGS 84 zone 18 N projection
inpr = pyproj.Proj('+proj=utm +zone=18 +ellps=WGS84 +datum=WGS84 +units=m +no_defs')

# WGS 84 projection
outpr = pyproj.Proj(init='epsg:4326')

par['holdridge'] = np.nan
par['chave_for'] = np.nan

def fortypes(row):
	lon, lat = pyproj.transform(inpr, outpr, row.X, row.Y)
	alt = allometry.altitude(lon, lat, elevation_rasters)
	prec = allometry.precipitation(lon, lat, precipitation_raster_folder)
	row_holdridge = allometry.holdridge_col(alt, prec)
	row_chave_for = allometry.chaveI_forest(prec)
	return (row_holdridge, row_chave_for)

par.loc[:, 'holdridge'], par.loc[:, 'chave_for'] = zip(*par.apply(fortypes, axis = 1))

# Compilar densidades
#
# Verificar todos los taxa producen densidades > 0
#
dens = wd(densities_file)



# Cargar Taxonomia

tax = pd.read_sql_table(table_name='Taxonomia', con = conn, index_col='TaxonID')

# Estimar biomasa por cada parcela

# columnas con valores de biomasa
par['alvarez'] = np.nan
par['chaveI'] = np.nan
par['chaveII'] = np.nan

# Estimacion coefficiente E de Chave
def estimate_E(row):
	lon, lat = pyproj.transform(inpr, outpr, row.X, row.Y)
	e_val = allometry.getE(lon, lat, chave_E_raster)
	return e_val

par['E'] = par.apply(estimate_E, axis=1)

# Clases de bosque para los cuales la ecuacion de alvarez funciona
alvhols = ['tropical_dry', 'tropical_moist', 'tropical_wet', 'premontane_moist', 'lower_montane_wet', 'montane_wet']
#
# Asignar aproximaciones a aquellas clase de bosque no consideradas por Alvarez
#

for pari in par[:10].itertuples():

	if pari.holdridge in alvhols:
		this_alvarez = 0
		this_chaveI = 0
		this_chaveII = 0

		query = "SELECT Diametro, Taxon FROM Individuos LEFT JOIN Determinaciones ON Dets=DetID WHERE Plot = {0}".format(pari.Index)

		meds = pd.read_sql_query(sql=query, con = conn)

		for ind in meds.itertuples():
			tax_accepted = ind.Taxon
			if not np.isnan(tax_accepted):
				dad = tax.loc[int(tax_accepted), 'SinonimoDe']
				while not np.isnan(dad):
					tax_accepted = dad
					dad = tax.loc[int(tax_accepted), 'SinonimoDe']

				family = tax.loc[tax_accepted, 'Familia']
				genus = tax.loc[tax_accepted, 'Genero']
				epithet = tax.loc[tax_accepted, 'Epiteto']

				twd = wd.get_density(family, genus, epithet, dens)

				this_alvarez += allometry.alvarez(ind.Diametro, twd, pari.holdridge)
				this_chaveI += allometry.chaveI(ind.Diametro, twd, pari.chave_for)

				#lon, lat = pyproj.transform(inpr, outpr, pari.X, pari.Y)
				this_chaveII += allometry.chaveII(ind.Diametro, twd, e_value = float(pari.E))

		par.loc[int(pari.Index) , 'alvarez'] = this_alvarez / pari.Area
		par.loc[int(pari.Index) , 'chaveI'] = this_chaveI / pari.Area
		par.loc[int(pari.Index) , 'chaveII'] = this_chaveII / pari.Area

conn.close()
