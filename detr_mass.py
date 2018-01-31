import pandas as pd
import sqlalchemy as al
import numpy as np
import wood_density as wd
import allometry


user = ''
password = ''
database = ''

engine = al.create_engine('mysql+mysqldb://{0}:{1}@localhost/{2}?charset=utf8&use_unicode=1&unix_socket=/var/run/mysqld/mysqld.sock'.format(user, password, database))

conn = engine.connect()

det = pd.read_sql_table("Detritos", con = conn, index_col="DetritoID")

det.drop(det[det.Diametro1.isna()].index, inplace=True)

det['DAP'] = np.nan
det.loc[det.Diametro2.isna(), 'DAP'] = det[det.Diametro2.isna()]['Diametro1']
det.loc[det.Diametro2.notna(), 'DAP'] = (det[det.Diametro2.notna()]['Diametro1'] + \
	det[det.Diametro2.notna()]['Diametro2']) / 2.0

congl = pd.read_sql_table(table_name='Conglomerados', con = conn, index_col='PlotID')

congl['Volumen_ha'] = 0.0
congl['Densidad_ha'] = 0.0

for congli in congl.itertuples():

	secc_count = 0
	for tr in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:

		for sec in range(1,4):

			if len(det[(det.Transecto == tr) & (det.Seccion == sec) & (det.Plot == int(congli.Index))]):

				# Verificar en cual extremo de las secciones de los transectos se realizaron las mediciones
				start = int()
				if len(det[(det.Transecto == tr) & (det.Seccion == sec) & (det.Plot == int(congli.Index)) & (det.Distancia >= 9)]) > len(det[(det.Transecto == tr) & (det.Seccion == sec) & (det.Plot == int(congli.Index)) & (det.Distancia <= 1)]):
					start = 9
				else:
					start = 0

				if len(det[(det.Transecto == tr) & (det.Seccion == sec) & (det.Plot == int(congli.Index)) & (det.Distancia >= start) & (det.Distancia <= (start + 1))]):

					th_dets = det[(det.Transecto == tr) & (det.Seccion == sec) & (det.Plot == int(congli.Index)) & (det.Distancia >= start) & (det.Distancia <= (start + 1))][['DAP','Inclinacion','Densidad']]

					th_dets = th_dets[th_dets.DAP.notna() & th_dets.Inclinacion.notna() & th_dets.Densidad.notna()]
					th_dets = th_dets[(th_dets.Inclinacion <= 85) & (th_dets.Inclinacion >= -85)]

					if len(th_dets) > 0:
						diams = th_dets.DAP.tolist()
						incls = th_dets.Inclinacion.tolist()
						dens = th_dets.Densidad.tolist()
						congl.loc[int(congli.Index) , 'Volumen_ha'] += allometry.det_vol(diams, 1, incls)
						congl.loc[int(congli.Index) , 'Densidad_ha'] += allometry.det_density(dens, diams, 1, incls)
						secc_count += 1

	if secc_count:
		congl.loc[int(congli.Index) , 'Volumen_ha'] /= secc_count
		congl.loc[int(congli.Index) , 'Densidad_ha'] /= secc_count

conn.close()
