import pandas as pd
import sqlalchemy as al
import numpy as np
import pyproj
import allometry
import wood_density as wd


user = ''
password = ''
database = ''

# Archivos (o carpetas) necesarios para los computos
densities_file = '/home/nelson/Documents/IDEAM/GlobalWoodDensityDB/gwddb_20180110.csv'

elevation_rasters = ('/home/nelson/Documents/GIS/Elevation/alt_30s_bil/alt.bil',)
#elevation_rasters = ('/home/nelsonsalinas/Documents/WorldClim/v1/alt/alt_23.tif', '/home/nelsonsalinas/Documents/WorldClim/v1/alt/alt_33.tif')
precipitation_raster_folder = '/home/nelson/Documents/IDEAM/WorldClim_v2/precipitation'
#precipitation_raster_folder = '/home/nelsonsalinas/Documents/WorldClim/v2/precipitation_30_sec'
chave_E_raster = '/home/nelson/Documents/IDEAM/Chave_E/E.bil'

engine = al.create_engine(
	'mysql+mysqldb://{0}:{1}@localhost/{2}?charset=utf8&use_unicode=1&unix_socket=/var/run/mysqld/mysqld.sock'.format(
	user, password, database))

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
dens = wd.load_data(densities_file)

# Cargar Taxonomia

tax = pd.read_sql_table(table_name='Taxonomia', con = conn)

tax['TaxonDef'] = np.int64

for t in tax.itertuples():
	tax_accepted = int(t.TaxonID)
	dad = t.SinonimoDe
	while pd.notna(dad):
		tax_accepted = int(dad)
		dad = tax[tax.TaxonID == tax_accepted]['SinonimoDe'].item()
	tax.loc[tax.TaxonID == t.TaxonID, 'TaxonDef' ] = tax_accepted


def density_updated(row):
	taxacc = row.TaxonDef
	fam = tax[tax.TaxonID == taxacc]['Familia'].item()
	gen = tax[tax.TaxonID == taxacc]['Genero'].item()
	epi = tax[tax.TaxonID == taxacc]['Epiteto'].item()
	return wd.get_density(fam, gen, epi, dens)

tax['Densidad'] = tax.apply(density_updated , axis =1)

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

# Clases de bosque son cambiado a una categoria cercana usada por Alvarez que produzca menor biomasa
forest_change = {'holdridge' : {'premontane_wet': 'lower_montane_wet',
'lower_montane_moist': 'lower_montane_wet',
'tropical_very_dry': 'tropical_dry',
'montane_moist': 'lower_montane_wet'}}

par.replace(to_replace = forest_change, inplace = True)

for pari in par[:10].itertuples():

	if pari.holdridge in alvhols:
		this_alvarez = 0
		this_chaveI = 0
		this_chaveII = 0

		query = "SELECT Diametro, Taxon FROM Individuos LEFT JOIN Determinaciones ON Dets=DetID WHERE Plot = {0}".format(pari.Index)

		meds = pd.read_sql_query(sql=query, con = conn)

		# densidad de madera promedio en la parcela
		avewd = 0.0
		avecount = 0
		for ttax in meds.Taxon.unique():
			twd = tax.loc[tax.loc[ttax, 'TaxonDef'], 'Densidad']
			if twd > 0:
				avewd += twd
				avecount += 1
		avewd /= avecount

		for ind in meds.itertuples():
			twd = tax.loc[tax.loc[ind.Taxon, 'TaxonDef'], 'Densidad']

			if twd == 0:
				twd = avewd

			this_alvarez += allometry.alvarez(ind.Diametro, twd, pari.holdridge)
			#lon, lat = pyproj.transform(inpr, outpr, pari.X, pari.Y)
			this_chaveII += allometry.chaveII(ind.Diametro, twd, e_value = float(pari.E))

		par.loc[int(pari.Index) , 'alvarez'] = this_alvarez / pari.Area
		par.loc[int(pari.Index) , 'chaveI'] = this_chaveI / pari.Area
		par.loc[int(pari.Index) , 'chaveII'] = this_chaveII / pari.Area

conn.close()
