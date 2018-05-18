import pandas as pd
import sqlalchemy as al
import numpy as np
import comm
import db_utils
from credentials import mysql_db

# Contenedor de resultados
outfile = 'biomass_IFN_2018_20180516.csv'
#outfile = 'biomass_IFN_2017_20180402.csv' 'Chave_II_d', 'Chave_II_dh', 'Alvarez_d', 'Alvarez_dh'
buffout = 'PlotID,Subparcela,Area_basal,Alvarez,Alvarez_dh,Chave_II,Chave_II_dh,Longitud,Latitud\n'

engine = al.create_engine( 'mysql+mysqldb://{0}:{1}@localhost/{2}?charset=utf8&use_unicode=1&unix_socket=/var/run/mysqld/mysqld.sock'.format(mysql_db['username'], mysql_db['password'], 'IFN_2018'))

#engine = al.create_engine( 'mysql+mysqldb://{0}:{1}@localhost/{2}?charset=utf8&use_unicode=1'.format(mysql_db['username'], mysql_db['password'], 'IFN_2018'))

conn = engine.connect()

# Archivos (o carpetas) necesarios para los computos
densities_file = '/home/nelson/Documents/IDEAM/wood_density_db/ChaveDB/gwddb_20180113.csv'
#densities_file = '/home/nelsonsalinas/Documents/wood_density_db/ChaveDB/gwddb_20180113.csv'

elevation_raster = '/home/nelson/Documents/IDEAM/cust_layers/alt/alt.tif'
#elevation_raster = '/home/nelsonsalinas/Documents/cust_layers/alt/alt.tif'

precipitation_raster = '/home/nelson/Documents/IDEAM/cust_layers/precp/precp.tif'
#precipitation_raster = '/home/nelsonsalinas/Documents/cust_layers/precp/precp.tif'

chave_E_raster = '/home/nelson/Documents/IDEAM/Chave_cartography/E.tif'
#chave_E_raster = '/home/nelsonsalinas/Documents/Chave_cartography/E.tif'

# Clases de bosque son cambiado a una categoria cercana usada por Alvarez que produzca menor biomasa
forest_change = {'holdridge' : {'premontane_wet': 'lower_montane_wet',
'lower_montane_moist': 'lower_montane_wet',
'tropical_very_dry': 'tropical_dry',
'montane_moist': 'lower_montane_wet'}}

taxacc = db_utils.acctax(conn)


query = "SELECT DiametroP AS Diameter, Tamano AS Size, AlturaTotal AS Height, Individuos.Plot as Plot, Subparcela AS Subplot, Taxon, Latitud, Longitud from Tallos LEFT JOIN Individuos ON IndividuoID = Individuo LEFT JOIN Determinaciones ON Dets = DetID WHERE Tamano IN ('L', 'F', 'FG') AND Dets IS NOT NULL AND PetrProf IS NULL AND PetrGolpes IS NULL"

trees = pd.read_sql_query(query, conn)

coors_or = pd.read_sql_table('Coordenadas', conn)
coors = coors_or[['Plot','Latitud','Longitud']].groupby('Plot').mean().reset_index()

trees = trees.merge(coors, how='left', on='Plot')

trees['Family'] = np.nan

trees['Genus'] = np.nan

trees['Epithet'] = np.nan

siar = {'L': 0.00283, 'F': 0.0154, 'FG': 0.0707}
side = {'L':2.5, 'F':10, 'FG':30}

for taxonid in taxacc:
	if pd.notna(taxacc[taxonid][0]):
		trees.loc[(trees.Taxon == taxonid), 'Family'] = taxacc[taxonid][0]
		if pd.notna(taxacc[taxonid][1]):
			trees.loc[(trees.Taxon == taxonid), 'Genus'] = taxacc[taxonid][1]
			if pd.notna(taxacc[taxonid][2]):
				trees.loc[(trees.Taxon == taxonid), 'Epithet'] = taxacc[taxonid][2]

for plotid in trees.Plot.unique(): #[158621]:

	if pd.notna(trees[trees.Plot == plotid]['Longitud'].iloc[0]) and pd.notna(trees[trees.Plot == plotid]['Latitud'].iloc[0]):

		myplot = comm.Plot(dataframe=trees[trees.Plot == plotid][['Family', 'Genus', 'Epithet', 'Diameter', 'Height', 'Subplot', 'Size']].copy(),
		size_area = siar, size_def = side)
		myplot.name = plotid
		fam, gen, spp = myplot.floristic_summary()
		if fam == 0: # Todos los individuos de las parcela estan indeterminados
			#print "Parcela {0} no fue analizada: No contiene ningun individuo determinado.".format(plotid)
			continue
		#print myplot.name
		myplot.purify()
		
		myplot.coordinates = trees[trees.Plot == plotid]['Longitud'].iloc[0], trees[trees.Plot ==  plotid]['Latitud'].iloc[0]
		
		for sps in range(1,6):
			myplot.coordinates_sps[sps] = coors[(coors['Plot'] == plotid) & (coors['SPF'] == sps)]['Longitud'].iloc[0], coors[(coors['Plot'] == plotid) & (coors['SPF'] == sps)]['Latitud'].iloc[0]
					
		myplot.set_holdridge(elevation_raster, precipitation_raster)

		if myplot.holdridge in forest_change['holdridge']:
			myplot.holdridge = forest_change['holdridge'][myplot.holdridge]

		myplot.set_chave_forest(precipitation_raster)

		myplot.set_E(chave_E_raster)
		#print myplot.E
		myplot.densities_from_file(densities_file)

		myplot.biomass(equations = ['Chave_II_d', 'Chave_II_dh', 'Alvarez_d', 'Alvarez_dh'])
		myplot.estimate_basal_area()
		
		#print myplot.chave_i
		#print '\n'
		
		for sps in myplot.basal_area_sps:
			buffout += "{0},{1},{2},{3},{4},{5},{6},{7}\n".format(myplot.name, sps, myplot.basal_area_sps[sps], myplot.alvarez_sps[sps], myplot.chave_i_sps[sps], myplot.chave_ii_sps[sps], myplot.coordinates_sps[sps][0], myplot.coordinates_sps[sps][1])
		
		#buffout += "{0},{1},{2},{3},{4},{5},{6}\n".format(myplot.name, myplot.basal_area, myplot.alvarez, myplot.chave_i, myplot.chave_ii, myplot.coordinates[0], myplot.coordinates[1])

with open(outfile, 'w') as fhandle:
	fhandle.write(buffout)

















#
