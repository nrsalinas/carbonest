import pandas as pd
import sqlalchemy as al
import numpy as np
import pyproj

"""
De Quimera db:
	1. Localización parcelas
		-Estimar clase de bosque y
	2. Datos dasométricos
"""

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

def fortypes(row, inproj, outproj):
	lon, lat = pyproj.transform(inproj, outproj, row.X, row.Y)
	alt = allometry.altitude(lon, lat, ('/home/nelsonsalinas/Documents/WorldClim/v1/alt/alt_23.tif',
        '/home/nelsonsalinas/Documents/WorldClim/v1/alt/alt_33.tif'))
	prep = allometry.precipitation(lon, lat, '/home/nelsonsalinas/Documents/WorldClim/v2/precipitation_30_sec')
	row.holdridge = allometry.holdridge_col(alt, prep)
	row.chave_for = allometry.chaveI_forest(prec)
	return None

par = par.apply(lambda x: fortypes(x, inpr, outpr))

# Compilar densidades

"""

for each taxon in densidades
	taxon not updated
	 	take the density as it is
	taxon updated
		check density source
			it is specific
				estimate new density
			it is genus average
				the genus was updated
					re-estimate density
				the genus was not updated
					take density as it is
			it is family average
				the family was updated
					re-estimate density
				the family was not updated
					take density as it is

"""



# Estimar biomasa por cada parcela
