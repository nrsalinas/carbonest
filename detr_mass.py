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

congl = pd.read_sql_table(table_name='Conglomerados', con = conn, index_col='PlotID')

congl['Volumen'] = 0.0

for congli in congl.itertuples():

	tran_count = 0
	for tr in trans:

		######################################################
		# Corregir secciones!!!
		######################################################
		if len(det[(det.Transecto == tr) & (det.Plot == int(congli.Index))]):

			# Verificar en cual extremo de las secciones de los transectos se realizaron las mediciones
			start = int()
			if len(det[(det.Transecto == tr) & (det.Plot == int(congli.Index)) & (det.Distancia >= 9)]) > len(det[(det.Transecto == tr) & (det.Plot == int(congli.Index)) & (det.Distancia <= 1)]):
				start = 9
			else:
				start = 0

			if len(det[(det.Transecto == tr) & (det.Plot == int(congli.Index)) & (det.Distancia >= start) & (det.Distancia <= (start + 1))]):

				diams = det[(det.Transecto == tr) & (det.Plot == int(congli.Index)) & (det.Distancia >= start) & (det.Distancia <= (start + 1))]['DAP'].tolist()
				diams = filter(lambda x: pd.notna(x), diams)

				incls = det[(det.Transecto == tr) & (det.Plot == int(congli.Index)) & (det.Distancia >= start) & (det.Distancia <= (start + 1))]['Inclinacion'].tolist()
				incls = filter(lambda x: pd.notna(x), incls)

				if len(diams) == len(incls) > 0:

					if diams and incls:

						diams, incls = zip(*filter(lambda x: 85 >= x[1] >= -85, zip(diams, incls)))

						if diams and incls:

							congl.loc[int(congli.Index) , 'Volumen'] += allometry.det_vol(diams, 1, incls)
							tran_count += 1

	congl.loc[int(congli.Index) , 'Volumen'] /= tran_count
