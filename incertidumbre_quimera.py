import pandas as pd
import numpy as np
import sqlalchemy as al
import db_utils
import comm
import pymc3
import pickle
import matplotlib.pyplot as plt
from scipy.stats import describe

# Iteraciones para la simulacion por fuste
iters = 100


# Cargar muestreo probabilidad posterior de los coefficientes de la ecuacion 
# de Chave et al. (2014).

trace = pickle.load(open("trace_20180224.pkl", "r"))

# Obtencion de un muestreo aleatorio de la distribucion posterior de los 
# coefficientes alometricos.
myas = np.random.choice(trace.get_values('a', burn = 1000, combine=True), iters)
myas = np.append(myas, myas.mean())
mybs = np.random.choice(trace.get_values('b', burn = 1000, combine=True), iters)
mybs = np.append(mybs, mybs.mean())
mycs = np.random.choice(trace.get_values('c', burn = 1000, combine=True), iters)
mycs = np.append(mycs, mycs.mean())
myds = np.random.choice(trace.get_values('d', burn = 1000, combine=True), iters)
myds = np.append(myds, myds.mean())
myes = np.random.choice(trace.get_values('e', burn = 1000, combine=True), iters)
myes = np.append(myes, myes.mean())


# Archivos raster

densities_file = '/home/nelsonsalinas/Documents/wood_density_db/ChaveDB/gwddb_20180113.csv'
#densities_file = '/home/nelson/Documents/IDEAM/wood_density_db/ChaveDB/gwddb_20180113.csv'

elevation_raster = '/home/nelsonsalinas/Documents/cust_layers/alt/alt.tif'
#elevation_raster = '/home/nelson/Documents/IDEAM/cust_layers/alt/alt.tif'

precipitation_raster = '/home/nelsonsalinas/Documents/cust_layers/precp/precp.tif'
#precipitation_raster = '/home/nelson/Documents/IDEAM/cust_layers/precp/precp.tif'

chave_E_raster = '/home/nelsonsalinas/Documents/Chave_cartography/E.tif'
#chave_E_raster = '/home/nelson/Documents/IDEAM/Chave_cartography/E.tif'


# Lectura de los datos dasometricos de la base de datos Quimera

user = ''
password = ''
database = ''

engine = al.create_engine(
	'mysql+mysqldb://{0}:{1}@localhost/{2}?charset=utf8&use_unicode=1&unix_socket=/var/run/mysqld/mysqld.sock'.format(
	user, password, database))

conn = engine.connect()


# Tabla de equivalencia taxonomica. Contiene dos columnas: ID del taxon y ID del taxon acceptado. 

accnames = db_utils.acctax(conn)

@profile
def mymain():
	for p in xrange(1, 2):

		# Tabla simple con todos los datos de una parcela: datos dasometricos, nombres de las especies y densidades.
		table = db_utils.dasotab('Quimera', conn, p, accepted_taxa = accnames)
		
		# Creaion de objeto comm.Plot para la manipulacion de datos.
		myplot = comm.Plot(dataframe=table)
		myplot.name = 1
		myplot.purify()
		myplot.coordinates = db_utils.coords('Quimera', conn, p)
		myplot.set_holdridge(elevation_raster, precipitation_raster)
		myplot.set_chave_forest(precipitation_raster)
		myplot.set_E(chave_E_raster)
		myplot.densities_from_file(densities_file)
		
		# Arrays multidimensionales de los datos simuladops. Cada fila contiene
		# los datos simulados para cada arbol
		AGB = []
		diamUnc = []
		wdUnc = []
		alloUnc = []


		for tree in myplot.stems.itertuples():
			AGB.append([])
			diamUnc.append([])
			wdUnc.append([])
			alloUnc.append([])
			
			# Incertidumbre del diametro
			sdd = tree.Diameter / 20.0
			diams = np.random.normal(tree.Diameter, sdd, iters)
			diams = np.append(diams, tree.Diameter)

			# Incertidumbre de la densidad de madera
			wd = myplot.taxa[myplot.taxa.TaxonID == tree.TaxonID]['Density'].item()
			sdwd = 0.07727873895528423
			wds = np.random.normal(wd, sdwd, iters)
			wds = np.append(wds, wd)

			# Incertidumbre total
			for sdi, swd, sa, sb, sc, sd, se in zip(diams[:-1], wds[:-1], myas[:-1], mybs[:-1], 
													mycs[:-1], myds[:-1], myes[:-1]):
				agb = sa + sb * myplot.E + sc * np.log(swd) + sd * np.log(sdi) + se * np.log(sdi)**2
				AGB[-1].append(agb)
			
			# Incertidumbre debida a los errores de diametro
			for sdi in diams[:-1]:
				agb = myas[-1] + mybs[-1] * myplot.E + mycs[-1] * np.log(wds[-1]) + myds[-1] * \
					np.log(sdi) + myes[-1] * np.log(sdi)**2
				diamUnc[-1].append(agb)

			# Incertidumbre debida a los errores de la densidad de madera
			for swd in wds[:-1]:
				agb = myas[-1] + mybs[-1] * myplot.E + mycs[-1] * np.log(swd) + myds[-1] * \
					np.log(diams[-1]) + myes[-1] * np.log(diams[-1])**2
				wdUnc[-1].append(agb)

			# Incertidumbre debida a los errores de la ecuacion alometrica
			for sa, sb, sc, sd, se in zip(myas[:-1], mybs[:-1], mycs[:-1], myds[:-1], myes[:-1]):
				agb = sa + sb * myplot.E + sc * np.log(wds[-1]) + sd * np.log(diams[-1]) + se * \
					np.log(diams[-1])**2
				alloUnc[-1].append(agb)

				
		AGB = np.array(AGB)
		diamUnc = np.array(diamUnc)
		wdUnc = np.array(wdUnc)
		alloUnc = np.array(alloUnc)


		# Muestreo combinatorio para obtener la biomasa de la parcela   
		path_sims = 10000

		total_agb = []
		for x in xrange(path_sims):
			this_agb = 0.0
			for t in xrange(AGB.shape[0]):
				this_agb += np.random.choice(AGB[t], 1)
			total_agb.append(this_agb[0])

		total_agb = np.empty((0, path_sims))
		for t in xrange(AGB.shape[0]):
			sample = np.random.choice(AGB[t], path_sims)
			sample = sample.reshape(1, path_sims)
			total_agb = np.append(total_agb , sample, axis=0)
		total_agb = total_agb.sum(axis=0)
			
		"""
		total_diam_unc = []
		for x in xrange(path_sims):
			this_agb = 0.0
			for t in xrange(diamUnc.shape[0]):
				this_agb += np.random.choice(diamUnc[t], 1)
			total_diam_unc.append(this_agb[0])

		total_wood_unc = []
		for x in xrange(path_sims):
			this_agb = 0.0
			for t in xrange(wdUnc.shape[0]):
				this_agb += np.random.choice(wdUnc[t], 1)
			total_wood_unc.append(this_agb[0])

		total_allo_unc = []
		for x in xrange(path_sims):
			this_agb = 0.0
			for t in xrange(alloUnc.shape[0]):
				this_agb += np.random.choice(alloUnc[t], 1)
			total_allo_unc.append(this_agb[0])
		"""
		
mymain()
