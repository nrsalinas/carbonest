################################################################################
#
# Estimacion de reservas de carbono total para el territorio colombiano.
# Archivos de entrada son dos tablas csv y dos archivos pickle.
# En las tablas csv se incluyen los los valores de biomasa por las diferentes
# parcelas (basicamente son el archivo de salida del script `calcc.py`).
# Los archivos pickle contienen los diccionarios con el conteo de pixeles de
# clase de bosque en Colombia. Tipicamente el archivo de salida del script
# `gis_rout.py`.
#
# El archivo de salida contiene las siguientes columnas:
# 1. Año
# 2. Sistema de clasificacion (Holdridge o Chave)
# 3. Ecuacion alometrica (alvarez, chaveI o chaveII)
# 4. Clase climática
# 5. Area (ha)
# 6. Biomasa (Ton)
#
################################################################################

import pandas as pd
import pickle

# Archivos de entrada
ifn_csv = "biomass_IFN_20180118.csv"
quimera_csv = "biomass_Quimera_20180118.csv"
forest_pixel_count_2015_file = "for_pix_count_2015.pkl"
forest_pixel_count_2016_file = "for_pix_count_2016.pkl"

# Archivo de salida
outfile = "report_2015-2016.csv"

px_area = 86.05507006173293 # Area de cada pixel, en hectareas
bffr = ""

ifn = pd.read_csv(ifn_csv)
ifn['DB'] = "IFN"
qui = pd.read_csv(quimera_csv)
qui['DB'] = "Quimera"

bio = pd.concat([ifn,qui])
bio = bio.reset_index(drop=True)
bio = bio.drop(bio[bio.alvarez.isna() | bio.chaveI.isna() | bio.chaveII.isna()].index)

# Conteo de pixeles de bosques 2016. Cada pixel corresponde a 0.008333333333 ** 2 grados
# = 0.8605507006173293 Km^2 = 86.05507006173293 ha
fc_2015 = pickle.load(open(forest_pixel_count_2015_file,"r"))
fc_2016 = pickle.load(open(forest_pixel_count_2016_file,"r"))

# Equivalencia de zonas de vida sin ecuaciones alometricas
for_eq = {
	'lower_montane_dry': 'lower_montane_wet',
	'lower_montane_moist': 'lower_montane_wet',
	'lower_montane_rain': 'lower_montane_wet',
	'lower_montane_wet': 'lower_montane_wet',
	'montane_moist': 'lower_montane_wet',
	'montane_wet': 'montane_wet',
	'premontane_moist': 'premontane_moist',
	'premontane_rain': 'lower_montane_wet',
	'premontane_wet': 'lower_montane_wet',
	'tropical_dry': 'tropical_dry',
	'tropical_moist': 'tropical_moist',
	'tropical_rain': 'tropical_wet',
	'tropical_very_dry': 'tropical_dry',
	'tropical_wet': 'tropical_wet'}

for fore in fc_2015['holdridge']:
	eq = for_eq[fore]
	if fore != eq:
		fc_2015['holdridge'][eq] += fc_2015['holdridge'][fore]
		fc_2015['holdridge'][fore] = 0

for fore in fc_2016['holdridge']:
	eq = for_eq[fore]
	if fore != eq:
		fc_2016['holdridge'][eq] += fc_2016['holdridge'][fore]
		fc_2016['holdridge'][fore] = 0



alv16 = 0.0
chI16 = 0.0
chII16 = 0.0

for syst in fc_2016:
	for forest in fc_2016[syst]:

		if fc_2016[syst][forest] > 0:

			if syst == 'chave_for':
				for_area = fc_2016[syst][forest] * px_area
				tot = bio[bio.chave_for == forest]['chaveI'].mean() * for_area * 0.001
				bffr += ",".join(map(str, [2016, syst, 'chaveI', forest, for_area, tot])) + "\n"
				if pd.notna(tot):
					chI16 += tot

			if syst == 'holdridge':
				for_area = fc_2016[syst][forest] * px_area
				tot = bio[bio.holdridge == forest]['alvarez'].mean() * for_area * 0.001
				bffr +=  ",".join(map(str, [2016, syst, 'alvarez', forest, for_area, tot])) + "\n"
				if pd.notna(tot):
					alv16 += tot
				for_area = fc_2016[syst][forest] * px_area
				tot = bio[bio.holdridge == forest]['chaveII'].mean() * for_area * 0.001
				bffr +=  ",".join(map(str, [2016, syst, 'chaveII', forest, for_area, tot])) + "\n"
				if pd.notna(tot):
					chII16 += tot

# Factor conversion biomasa a carbono
alv16 *= 0.5
chI16 *= 0.5
chII16 *= 0.5

alv15 = 0.0
chI15 = 0.0
chII15 = 0.0

for syst in fc_2015:
	for forest in fc_2015[syst]:

		if fc_2015[syst][forest] > 0:

			if syst == 'chave_for':
				for_area =  fc_2015[syst][forest] * px_area
				tot = bio[bio.chave_for == forest]['chaveI'].mean() * for_area * 0.001
				bffr += ",".join(map(str, [2015, syst, 'chaveI', forest, for_area, tot])) + "\n"
				if pd.notna(tot):
					chI15 += tot

			if syst == 'holdridge':
				for_area =  fc_2015[syst][forest] * px_area
				tot = bio[bio.holdridge == forest]['alvarez'].mean() * for_area * 0.001
				bffr += ",".join(map(str, [2015, syst, 'alvarez', forest, for_area, tot])) + "\n"
				if pd.notna(tot):
					alv15 += tot
				for_area =  fc_2015[syst][forest] * px_area
				tot = bio[bio.holdridge == forest]['chaveII'].mean() * for_area * 0.001
				bffr += ",".join(map(str, [2015, syst, 'chaveII', forest, for_area, tot])) + "\n"
				if pd.notna(tot):
					chII15 += tot

with open(outfile, "w") as fh:
	fh.write(bffr)

# Factor conversion biomasa a carbono
alv15 *= 0.5
chI15 *= 0.5
chII15 *= 0.5
