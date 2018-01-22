################################################################################
#
# Estimación de biomasa arborea a partir de datos de vegetación contenidos
# en las bases de datos IFN y Quimera del SMBYC - IDEAM.
#
# El output de la ejecucion del presente script es una tabla en formato
# csv que contiene:
# 1. el indice de la parcela dentro de la base de datos
# 2. longitud
# 3. latitud
# 4. zona de vida de Holdridge
# 5. clase de bosque de acuerdo a Chave et al. 2005
# 6. densidad de carbono, ecuacion de Alvarez et al. 2012 (tons / ha)
# 7. densidad de carbono, ecuacion de Chave et al. 2005 (tons / ha)
# 8. densidad de carbono, ecuacion de Chave et al. 2014 (tons / ha)
#
# El nombre del archivo de salida se declara con la variable `outfile`.
#
################################################################################

import pandas as pd
import sqlalchemy as al
import numpy as np
import pyproj
import allometry
import wood_density as wd

# Variables de configuración de acceso a la base de datos
user = ''
password = ''
database = ''

# Nombre del archivo output
#outfile = 'biomass_Quimera_20180118.csv'
outfile = 'biomass_IFN_20180118.csv'

# Archivos (o carpetas) necesarios para los computos
#densities_file = '/home/nelson/Documents/IDEAM/GlobalWoodDensityDB/gwddb_20180113.csv'
densities_file = '/home/nelsonsalinas/Documents/wood_density_db/ChaveDB/gwddb_20180113.csv'

#elevation_raster = '/home/nelson/Documents/IDEAM/cust_layers/alt.tif'
elevation_raster = '/home/nelsonsalinas/Documents/cust_layers/alt/alt.tif'

#precipitation_raster = '/home/nelson/Documents/IDEAM/cust_layers/precp.tif'
precipitation_raster = '/home/nelsonsalinas/Documents/cust_layers/precp/precp.tif'

#chave_E_raster = '/home/nelson/Documents/IDEAM/Chave_E/E.bil'
chave_E_raster = '/home/nelsonsalinas/Documents/Chave_cartography/E.tif'

engine = al.create_engine(
	'mysql+mysqldb://{0}:{1}@localhost/{2}?charset=utf8&use_unicode=1&unix_socket=/var/run/mysqld/mysqld.sock'.format(
	user, password, database))

conn = engine.connect()

# WGS 84 zone 18 N projection
inpr = pyproj.Proj('+proj=utm +zone=18 +ellps=WGS84 +datum=WGS84 +units=m +no_defs')

# WGS 84 projection
outpr = pyproj.Proj(init='epsg:4326')

def conv_coors(row, dim_out):
	out = None
	lon, lat = pyproj.transform(inpr, outpr, row.X, row.Y)
	if dim_out == 'Lat':
		out = lat
	elif dim_out == 'Lon':
		out = lon
	return out

par = None
if database == "Quimera":
	par = pd.read_sql_table(table_name='Parcelas', con = conn, index_col='PlotID')
	par['Longitud'] = par.apply(lambda x: conv_coors(x, dim_out = 'Lon'), axis=1)
	par['Latitud'] = par.apply(lambda x: conv_coors(x, dim_out = 'Lat'), axis=1)

elif database == "IFN":
	par = pd.read_sql_table(table_name='Conglomerados', con = conn)
	coors = pd.read_sql_table(table_name='Coordenadas', con = conn)
	coors = coors.rename(columns={'Plot':'PlotID'})
	par = par.merge(coors[coors.SPF == 1][['Longitud', 'Latitud', 'PlotID']], on='PlotID', how='left')
	par = par.set_index('PlotID')


par['holdridge'] = np.nan
par['chave_for'] = np.nan

def holdtypes(row):
	alt = allometry.altitude(row.Longitud, row.Latitud, elevation_raster)
	prec = allometry.precipitation(row.Longitud, row.Latitud, precipitation_raster)
	row_holdridge = allometry.holdridge_col(alt, prec)
	return row_holdridge

def chavetypes(row):
	prec = allometry.precipitation(row.Longitud, row.Latitud, precipitation_raster)
	row_chave_for = allometry.chaveI_forest(prec)
	return row_chave_for

par['holdridge'] = par.apply(holdtypes, axis=1)
par['chave_for'] = par.apply(chavetypes, axis = 1)

# Compilar densidades
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

# Las siguientes familias son taxa prodominantemente no arboreos y son excluidos de los computos
herb_families =  [u'Aizoaceae', u'Alstroemeriaceae', u'Araceae', u'Aristolochiaceae', u'Athyriaceae', u'Blechnaceae', u'Campanulaceae', u'Commelinaceae', u'Cucurbitaceae', u'Cyatheaceae', u'Cyclanthaceae', u'Cyperaceae', u'Dennstaedtiaceae', u'Dicksoniaceae', u'Dryopteridaceae', u'Francoaceae', u'Gesneriaceae', u'Gunneraceae', u'Heliconiaceae', u'Lomariopsidaceae', u'Marantaceae', u'Marcgraviaceae', u'Musaceae', u'Orchidaceae', u'Poaceae', u'Pteridaceae', u'Smilacaceae', u'Strelitziaceae', u'Woodsiaceae', u'Zingiberaceae']

herb_tax_def = tax.loc[tax.Familia.isin(herb_families), 'TaxonDef'].tolist()


def density_updated(row):
	taxacc = row.TaxonDef
	fam = tax[tax.TaxonID == taxacc]['Familia'].item()
	gen = tax[tax.TaxonID == taxacc]['Genero'].item()
	epi = tax[tax.TaxonID == taxacc]['Epiteto'].item()
	return wd.get_density(fam, gen, epi, dens)

tax['Densidad'] = tax.apply(density_updated , axis =1)

# Estimacion coefficiente E de Chave
def estimate_E(row):
	e_val = allometry.getE(row.Longitud, row.Latitud, chave_E_raster)
	return e_val

par['E'] = par.apply(estimate_E, axis=1)

# Clases de bosque son cambiado a una categoria cercana usada por Alvarez que produzca menor biomasa
forest_change = {'holdridge' : {'premontane_wet': 'lower_montane_wet',
'lower_montane_moist': 'lower_montane_wet',
'tropical_very_dry': 'tropical_dry',
'montane_moist': 'lower_montane_wet'}}

par.replace(to_replace = forest_change, inplace = True)

# TaxonID de indet absoluto
NNID = tax.loc[tax.Familia.isna() & tax.Genero.isna() & tax.Epiteto.isna(), 'TaxonID'].item()
par_skipped = []

area_ifn = {'L':28.3, 'F':153.9, 'FG':706.9}

# columnas con valores de biomasa
par['alvarez'] = np.nan
par['chaveI'] = np.nan
par['chaveII'] = np.nan

for pari in par.itertuples():

	this_alvarez = 0
	this_chaveI = 0
	this_chaveII = 0

	if database == "Quimera":
		query = "SELECT Diametro, Taxon, IndividuoID FROM Individuos LEFT JOIN Determinaciones ON Dets=DetID WHERE Plot = {0}".format(pari.Index)

	elif database == "IFN":
		# Individuos sin Dets son muetos en pie no identificados
		query = "SELECT DiametroP AS Diametro, Tamano, Taxon, TalloID, IndividuoID FROM Tallos LEFT JOIN Individuos ON Individuo = IndividuoID LEFT JOIN Determinaciones ON Dets=DetID WHERE Plot = {0} AND Dets IS NOT NULL AND Tamano IN ('L', 'F', 'FG')".format(pari.Index)

	meds = pd.read_sql_query(sql=query, con = conn)


	# densidad de madera promedio en la parcela
	avewd = 0.0
	avecount = 0

	# Eliminar taxa herbarceos
	meds.drop(meds[meds.Taxon.isin(herb_tax_def)].index, inplace = True)

	if meds.shape[0] == 0:
		par_skipped.append(pari.Index)
		continue

	# Si ningun individuo esta determinado pasar a la siguiente parcela
	if len(filter(lambda x: tax.loc[tax.TaxonID == int(x), 'TaxonDef'].item() != NNID, meds.Taxon.unique())) == 0:
		par_skipped.append(pari.Index)
		continue

	for tree in meds.itertuples():
		if len(tax.loc[tax.TaxonID == tree.Taxon, 'Densidad']) == 1:
			if pd.notna(tax.loc[tax.TaxonID == tree.Taxon, 'Densidad'].item()):
				avewd += tax.loc[tax.TaxonID == tree.Taxon, 'Densidad'].item()
				avecount += 1
		elif len(tax.loc[tax.TaxonID == tree.Taxon, 'Densidad']) > 1:
			print "\t{0} has {1} densities in tax table.".format(tree.Taxon,
					len(tax.loc[tax.TaxonID == tree.Taxon, 'Densidad']))
	if avecount > 0:
		avewd /= avecount

	if avewd == 0:
		print "avewd is zero"

	for tree in meds.itertuples():
		twd = 0
		if tree.Diametro <= 0:
			print "Individuo {0} tiene diametro ilegal.".format(tree.IndividuoID)
		if len(tax.loc[tax.TaxonID == tree.Taxon, 'Densidad']) == 1:
			if pd.notna(tax.loc[tax.TaxonID == tree.Taxon, 'Densidad'].item()):
				twd = tax.loc[tax.TaxonID == tree.Taxon, 'Densidad'].item()
			else:
				twd = avewd
				ttaxdef = tax.loc[tax.TaxonID == tree.Taxon, 'TaxonDef'].item()

			if twd <= 0:
				print "Density is illegal"

			area = float()
			if database == "Quimera":
				area = pari.Area
			elif database == "IFN":
				area = area_ifn[tree.Tamano] / 2000

			try:
				this_alvarez += allometry.alvarez(tree.Diametro, twd, pari.holdridge) / area
				#lon, lat = pyproj.transform(inpr, outpr, pari.X, pari.Y)
				this_chaveII += allometry.chaveII(tree.Diametro, twd, e_value = float(pari.E)) / area
				this_chaveI += allometry.chaveI(tree.Diametro, twd, pari.chave_for) / area
			except:
				print "Plot: {0}, Individuo: {1}, Taxon: {2}, Diametro: {3}, Densidad: {4}, E: {5}".format(pari.Index, tree.IndividuoID, tree.Taxon, tree.Diametro, twd, pari.E)


	par.loc[int(pari.Index) , 'alvarez'] = this_alvarez
	par.loc[int(pari.Index) , 'chaveI'] = this_chaveI
	par.loc[int(pari.Index) , 'chaveII'] = this_chaveII



conn.close()

par[['Longitud','Latitud','holdridge','chave_for','alvarez','chaveI','chaveII']].to_csv(outfile, index_label='PlotID')
