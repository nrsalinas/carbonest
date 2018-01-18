import pandas as pd
import pickle

ifn = pd.read_csv("biomass_IFN_20180118.csv")
qui = pd.read_csv("biomass_Quimera_20180118.csv")

bio = pd.concat([ifn,qui])
bio = bio.reset_index(drop=True)
bio = bio.drop(bio[bio.alvarez.isna() | bio.chaveI.isna() | bio.chaveII.isna()].index)

# Conteo de pixeles de bosques 2016. Cada pixel corresponde a 0.008333333333 ** 2 grados
# = 0.8605507006173293 Km^2 = 86.05507006173293 ha
fc_2016 = pickle.load(open("for_pix_count_2016.pkl","r"))
fc_2015 = pickle.load(open("for_pix_count_2015.pkl","r"))
px_area = 86.05507006173293


alv16 = 0.0
chI16 = 0.0
chII16 = 0.0

for syst in fc_2016:
	for forest in fc_2016[syst]:

		if syst == 'chave_for':
			tot = bio[bio.chave_for == forest]['chaveI'].mean() * fc_2016[syst][forest] * px_area
			print syst, forest, tot
			if pd.notna(tot):
				chI16 += tot

		if syst == 'holdridge':
			tot = bio[bio.holdridge == forest]['alvarez'].mean() * fc_2016[syst][forest] * px_area
			print syst, forest, tot
			if pd.notna(tot):
				alv16 += tot
			tot = bio[bio.holdridge == forest]['chaveII'].mean() * fc_2016[syst][forest] * px_area
			print syst, forest, tot
			if pd.notna(tot):
				chII16 += tot

# Factor conversion biomasa a carbono
alv16 *= 0.5
chI16 *= 0.5
chII16 *= 0.5
# Conversion a toneladas
alv16 *= 0.001
chI16 *= 0.001
chII16 *= 0.001


alv15 = 0.0
chI15 = 0.0
chII15 = 0.0

for syst in fc_2015:
	for forest in fc_2015[syst]:

		if syst == 'chave_for':
			tot = bio[bio.chave_for == forest]['chaveI'].mean() * fc_2015[syst][forest] * px_area
			print syst, forest, tot
			if pd.notna(tot):
				chI15 += tot

		if syst == 'holdridge':
			tot = bio[bio.holdridge == forest]['alvarez'].mean() * fc_2015[syst][forest] * px_area
			print syst, forest, tot
			if pd.notna(tot):
				alv15 += tot
			tot = bio[bio.holdridge == forest]['chaveII'].mean() * fc_2015[syst][forest] * px_area
			print syst, forest, tot
			if pd.notna(tot):
				chII15 += tot

# Factor conversion biomasa a carbono
alv15 *= 0.5
chI15 *= 0.5
chII15 *= 0.5
# Conversion a toneladas
alv15 *= 0.001
chI15 *= 0.001
chII15 *= 0.001
