import pandas as pd
import sqlalchemy as al
import numpy as np
import wood_density as wd
import allometry


user = 'root'
password = 'Soledad1'
database = 'IFN'

trans = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']


engine = al.create_engine('mysql+mysqldb://{0}:{1}@localhost/{2}?charset=utf8&use_unicode=1&unix_socket=/var/run/mysqld/mysqld.sock'.format(user, password, database))
conn = engine.connect()

det = pd.read_sql_table("Detritos", con = conn, index_col="DetritoID")

det.drop(det[det.Diametro1.isna()].index, inplace=True)

det['DAP'] = np.nan
det.loc[det.Diametro2.isna(), 'DAP'] = det[det.Diametro2.isna()]['Diametro1']
det.loc[det.Diametro2.notna(), 'DAP'] = (det[det.Diametro2.notna()]['Diametro1'] + \
    det[det.Diametro2.notna()]['Diametro2']) / 2.0
#
# Para cada parcela
#

# Verificar en cual extremo de las secciones de los transectos se realizaron las mediciones
for tr in trans:

	start = int()
	if len(det[(det.Transecto == tr) & (det.Plot == 7921) & (det.Distancia >= 9)]) > len(det[(det.Transecto == tr) & (det.Plot == 7921) & (det.Distancia <= 1)]):
	    start = 9
	else:
	    start = 0

	if len(det[(det.Transecto == tr) & (det.Plot == 7921) & (det.Distancia >= start) & (det.Distancia <= (start + 1))]):

		diams = det[(det.Transecto == tr) & (det.Plot == 7921) & (det.Distancia >= start) & (det.Distancia <= (start + 1))]['DAP'].tolist()

		incls = det[(det.Transecto == tr) & (det.Plot == 7921) & (det.Distancia >= start) & (det.Distancia <= (start + 1))]['Inclinacion'].tolist()

		diams, incls = zip(*filter(lambda x: not x[0] is None and not x[1] is None, zip(diams, incls)))

		vol = allometry.det_vol(diams, 1, incls)
