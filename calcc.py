import pandas as pd
import sqlalchemy as al
import numpy as np
import pyproj
import allometry
import wood_density as wd


user = ''
password = ''
database = ''

# Conteo de pixeles de bosques 2016. Cada pixel corresponde a 0.008333333333 ** 2
# grados = 0.8605475872847063 km^2
for_type_count = {
'chaveI':
	{'dry': 16247, 'moist': 600836, 'wet': 75316},

'holdrigde':
	{'lower_montane_dry': 116,
	'lower_montane_moist': 20510,
	'lower_montane_rain': 1,
	'lower_montane_wet': 13994,
	'montane_moist': 385,
	'montane_wet': 10537,
	'premontane_moist': 15677,
	'premontane_rain': 200,
	'premontane_wet': 26985,
	'tropical_dry': 7689,
	'tropical_moist': 544705,
	'tropical_rain': 1,
	'tropical_very_dry': 594,
	'tropical_wet': 51005}}

# Archivos (o carpetas) necesarios para los computos
densities_file = '/home/nelson/Documents/IDEAM/GlobalWoodDensityDB/gwddb_20180113.csv'
#densities_file = '/home/nelsonsalinas/Documents/wood_density_db/ChaveDB/gwddb_20180113.csv'

elevation_rasters = ('/home/nelson/Documents/IDEAM/cust_layers/alt.tif',)
#elevation_rasters = ('/home/nelsonsalinas/Documents/WorldClim/v1/alt/alt_23.tif', '/home/nelsonsalinas/Documents/WorldClim/v1/alt/alt_33.tif')
precipitation_raster = '/home/nelson/Documents/IDEAM/cust_layers/precp.tif'
#precipitation_raster_folder = '/home/nelsonsalinas/Documents/WorldClim/v2/precipitation_30_sec'
chave_E_raster = '/home/nelson/Documents/IDEAM/Chave_E/E.bil'
#chave_E_raster = '/home/nelsonsalinas/Documents/Chave_cartography/E.tif'

engine = al.create_engine(
	'mysql+mysqldb://{0}:{1}@localhost/{2}?charset=utf8&use_unicode=1&unix_socket=/var/run/mysqld/mysqld.sock'.format(
	user, password, database))

conn = engine.connect()

par = None
if database == "Quimera":
	par = pd.read_sql_table(table_name='Parcelas', con = conn, index_col='PlotID')

elif database == "IFN":
	par = pd.read_sql_table(table_name='Conglomerados', con = conn)
	coors = pd.read_sql_table(table_name='Coordenadas', con = conn)
	coors = coors.rename(columns={'Plot':'PlotID'})
	par = par.merge(coors[coors.SPF == 1][['Longitud', 'Latitud', 'PlotID']], on='PlotID', how='left')
	par = par.set_index('PlotID')


# WGS 84 zone 18 N projection
inpr = pyproj.Proj('+proj=utm +zone=18 +ellps=WGS84 +datum=WGS84 +units=m +no_defs')

# WGS 84 projection
outpr = pyproj.Proj(init='epsg:4326')

par['holdridge'] = np.nan
par['chave_for'] = np.nan

def holdtypes(row):
	lon, lat = float(), float()
	if database == "IFN":
		lon = row.Longitud
		lat = row.Latitud
	elif database == "Quimera":
		lon, lat = pyproj.transform(inpr, outpr, row.X, row.Y)
	alt = allometry.altitude(lon, lat, elevation_rasters)
	prec = allometry.precipitation(lon, lat, precipitation_raster)
	row_holdridge = allometry.holdridge_col(alt, prec)
	return row_holdridge

def chavetypes(row):
	lon, lat = float(), float()
	if database == "IFN":
		lon = row.Longitud
		lat = row.Latitud
	elif database == "Quimera":
		lon, lat = pyproj.transform(inpr, outpr, row.X, row.Y)
	prec = allometry.precipitation(lon, lat, precipitation_raster)
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

# columnas con valores de biomasa
par['alvarez'] = np.nan
par['chaveI'] = np.nan
par['chaveII'] = np.nan

# Estimacion coefficiente E de Chave
def estimate_E(row):
	lon, lat = int(), int()
	if database == "Quimera":
		lon, lat = pyproj.transform(inpr, outpr, row.X, row.Y)
	elif database == "IFN":
		lon = row.Longitud
		lat = row.Latitud
	e_val = allometry.getE(lon, lat, chave_E_raster)
	return e_val

par['E'] = par.apply(estimate_E, axis=1)

# Clases de bosque para los cuales la ecuacion de alvarez funciona
#alvhols = ['tropical_dry', 'tropical_moist', 'tropical_wet', 'premontane_moist', 'lower_montane_wet', 'montane_wet']

# Clases de bosque son cambiado a una categoria cercana usada por Alvarez que produzca menor biomasa
forest_change = {'holdridge' : {'premontane_wet': 'lower_montane_wet',
'lower_montane_moist': 'lower_montane_wet',
'tropical_very_dry': 'tropical_dry',
'montane_moist': 'lower_montane_wet'}}

par.replace(to_replace = forest_change, inplace = True)

# TaxonID de indet absoluto
NNID = tax.loc[tax.Familia.isna() & tax.Genero.isna() & tax.Epiteto.isna(), 'TaxonID'].item()
par_skipped = []
#failed_par = [182, 183, 484]
#for pari in par.itertuples():
for pari in par[:20].itertuples():
	#print pari.Index
	#if pari.holdridge in alvhols:

	this_alvarez = 0
	this_chaveI = 0
	this_chaveII = 0

	if database == "Quimera":
		"SELECT Diametro, Taxon, IndividuoID FROM Individuos LEFT JOIN Determinaciones ON Dets=DetID WHERE Plot = {0}".format(pari.Index)
	elif database == "IFN":
		######################################################################
		# Resolver Individuos con Dets = NULL
		######################################################################
		query = "SELECT DiametroP AS Diametro, Taxon, TalloID, IndividuoID FROM Tallos LEFT JOIN Individuos ON Individuo = IndividuoID LEFT JOIN Determinaciones ON Dets=DetID WHERE Plot = {0} AND Dets IS NOT NULL".format(pari.Index)

	meds = pd.read_sql_query(sql=query, con = conn)


	# densidad de madera promedio en la parcela
	avewd = 0.0
	avecount = 0

	# Eliminar taxa herbarceos
	meds.drop(meds[meds.Taxon.isin(herb_tax_def)].index, inplace = True)

	if meds.shape[0] == 0:
		par_skipped.append(pari.Index)
		continue

	print meds.Taxon.unique()
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
	#print "average wood density: {0} (based on {1} individuals)".format(avewd, avecount)

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
				#print tax.loc[tax.TaxonID == ttaxdef, 'Familia'].item(),
				#print tax.loc[tax.TaxonID == ttaxdef, 'Genero'].item(),
				#print tax.loc[tax.TaxonID == ttaxdef, 'Epiteto'].item(),"got no wood density"

			if twd <= 0:
				print "Density is illegal"

			try:
				this_alvarez += allometry.alvarez(tree.Diametro, twd, pari.holdridge)
				#lon, lat = pyproj.transform(inpr, outpr, pari.X, pari.Y)
				this_chaveII += allometry.chaveII(tree.Diametro, twd, e_value = float(pari.E))
				this_chaveI += allometry.chaveI(tree.Diametro, twd, pari.chave_for)
			except:
				print "Plot: {0}, Individuo: {1}, Taxon: {2}, Diametro: {3}, Densidad: {4}, E: {5}".format(pari.Index, tree.IndividuoID, tree.Taxon, tree.Diametro, twd, pari.E)

	area = float()
	if database == "Quimera":
		area = pari.Area
	else:
		area = 28.3 # or 154 or 707

	par.loc[int(pari.Index) , 'alvarez'] = this_alvarez / area
	par.loc[int(pari.Index) , 'chaveI'] = this_chaveI / area
	par.loc[int(pari.Index) , 'chaveII'] = this_chaveII / area



conn.close()

par[['alvarez','chaveI','chaveII']].to_csv('biomass_quimera_20180117.csv', index_label='PlotID')
