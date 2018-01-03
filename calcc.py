import pandas as pd
import sqlalchemy as al
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

for_types = {}
for row in par.itertuples():
	lon, lat = pyproj.transform(inpr, outpr, row.X, row.Y)
	alt = allometry.altitude(lon, lat, ('/home/nelsonsalinas/Documents/WorldClim/v1/alt/alt_23.tif',
        '/home/nelsonsalinas/Documents/WorldClim/v1/alt/alt_33.tif'))
	prep = allometry.precipitation(lon, lat, '/home/nelsonsalinas/Documents/WorldClim/v2/precipitation_30_sec')
	hold = allometry.holdridge_col(alt, prep)
	for_types[hold] = 0
	if hold is None:
		print alt, prep, lon, lat
