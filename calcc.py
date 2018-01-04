import pandas as pd
import sqlalchemy as al
import numpy as np
import pyproj
import allometry


user = ''
password = ''
database = ''

engine = al.create_engine('mysql+mysqldb://{0}:{1}@localhost/{2}?charset=utf8&use_unicode=1'.format(user, password, database))

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
	alt = allometry.altitude(lon, lat, ('/home/nelsonsalinas/Documents/WorldClim/v1/alt/alt_23.tif',
        '/home/nelsonsalinas/Documents/WorldClim/v1/alt/alt_33.tif'))
	prec = allometry.precipitation(lon, lat, '/home/nelsonsalinas/Documents/WorldClim/v2/precipitation_30_sec')
	row_holdridge = allometry.holdridge_col(alt, prec)
	row_chave_for = allometry.chaveI_forest(prec)
	return (row_holdridge, row_chave_for)

par.loc[:, 'holdridge'], par.loc[:, 'chave_for'] = zip(*par.apply(fortypes, axis = 1))

# Compilar densidades


# Cargar Taxonomia

tax = pd.read_sql_table(table_name='Taxonomia', con = conn, index_col='TaxonID')

# Estimar biomasa por cada parcela

for parita in par.itertuples():
	query = "SELECT Diametro, Taxon FROM Individuos LEFT JOIN Determinaciones ON Dets=DetID WHERE Plot = {0}".format(par.PlotID)

	meds = pd.read_sql_query(sql=query, con = conn)

	for ind in meds.itertuples():

		acctax = np.nan
		while np.isnan(acctax):
