import pandas as pd
import numpy as np
import allometry
import wood_density as wd

class Plot(object):
	"""
	Main data structure for tree ecological data.

	Arguments:

	- csv_file (str): Path to a csv file containing the vegetation data.

	- dataframe (pd.Dataframe): Pandas dataframe containing the vegetation data.

		The vegetation data should contain the following columns:

		- `Family` (APG IV classification system)
		- `Genus`
		- `Epithet`
		- `Diameter` (cm)
		- `Height` (m)

		For taxonomic columns, empty cells (csv) or pd.nan values (dataframe)
		indicate indetetermined hierarchy. The following columns are optional:

		- `Subplot`
		- `StemID`
		- `Size` (stem size category)

		If size categories were employed, their definitions and effective sampling
		area should be parse through the `size_def` and `size_area` arguments.

	- size_def (dict): Stem size definitions. Keys are size codes (str) and values
	the lower DAP limit (cm) of the category (float).

	- size_area (dict): Stem size effective areas. Keys are size codes (str) and
	values the sampling area (ha) of the category (float). If the plot is divided
	in subplots areas should correspond to the effective area per subplot, otherwise
	it will be assumed they are the total effective area per category in the plot.

	"""
	def __init__(self, csv_file = None, dataframe = None, size_def = None,
		size_area = None):

		if csv_file is None and dataframe is None:
			raise ValueError("Plot could not be instantiated: no data was parsed.")

		elif csv_file:
			pass

		elif isinstance(dataframe, pd.DataFrame):

			self.name = None # Plot identifier (e.g., index)
			self.coordinates = None
			self.coordinates_sps = {}

			self.holdridge = None
			self.chave_forest = None

			self.E = None
			self.elevation = None
			self.precipitation = None

			self.size_def = None
			self.size_area = None # Effective sampled area per diametric class
			self.area = None # Total area
			
			self.basal_area = None
			self.basal_area_sps = {}

			self.alvarez_d = 0.0 # Tons / ha
			self.alvarez_d_sps = {}
			self.alvarez_dh = 0.0 # Tons / ha
			self.alvarez_dh_sps = {}
			self.chave_i_ = 0.0 # Tons / ha
			self.chave_i_sps = {}
			self.chave_ii_d = 0.0 # Tons / ha
			self.chave_ii_d_sps = {}
			self.chave_ii_dh = 0.0 # Tons / ha
			self.chave_ii_dh_sps = {}
			# optional fields
			fields = ['Diameter','Height','TaxonID']

			if 'Subplot' in dataframe.columns:
				fields.append('Subplot')
				self.basal_area_sps = {c: 0.0 for c in dataframe.Subplot.unique()}
				#print self.basal_area_sps
				self.alvarez_d_sps = {c: 0.0 for c in dataframe.Subplot.unique()}
				self.alvarez_dh_sps = {c: 0.0 for c in dataframe.Subplot.unique()}
				#print self.alvarez_sps
				self.chave_i_sps = {c: 0.0 for c in dataframe.Subplot.unique()}
				#print self.chave_i_sps
				self.chave_ii_d_sps = {c: 0.0 for c in dataframe.Subplot.unique()}
				self.chave_ii_dh_sps = {c: 0.0 for c in dataframe.Subplot.unique()}
				#print self.chave_ii_sps
				self.coordinates_sps = {c: (None, None) for c in dataframe.Subplot.unique()}
				#print self.coordinates_sps
				
			if 'StemID' in dataframe.columns:
				fields.append('StemID')

			if 'Size' in dataframe.columns and size_def and size_area:
				fields.append('Size')
				self.size_def = size_def
				self.size_area = size_area

			dataframe.loc[:,['Family','Genus', 'Epithet']] = dataframe[['Family','Genus',
				'Epithet']].fillna('INDET')


			self.taxa = dataframe.groupby(['Family','Genus','Epithet']).size().reset_index(
				).drop(columns=0).copy()

			self.taxa['TaxonID'] = self.taxa.index

			self.stems = dataframe.merge(self.taxa, on=['Family','Genus','Epithet'], how='left'
				)[fields].copy()

			self.taxa.replace(to_replace='INDET', value=np.nan, inplace=True)

			dataframe.replace(to_replace='INDET', value=np.nan, inplace=True)


	def floristic_summary(self, no_indets = False):
		"""
		Estimates the number of families, genera and species in the plot.
		"""
		fully_indets = self.taxa[self.taxa.Family.isna() & self.taxa.Genus.isna() & self.taxa.Epithet.isna()].shape[0]

		fam = self.taxa[self.taxa.Family.notna()]["Family"].unique().shape[0]
		gen = 0
		spp = 0

		if no_indets:
			gen = self.taxa[self.taxa.Family.notna() & self.taxa.Genus.notna()]["Genus"].unique().shape[0]

			spp = self.taxa[self.taxa.Family.notna() & self.taxa.Genus.notna() & self.taxa.Epithet.notna()].shape[0]

		else:
			gen = 0
			for fami in self.taxa[self.taxa.Family.notna()]["Family"].unique().tolist():
				gen += self.taxa[(self.taxa.Family == fami)]["Genus"].unique().shape[0]

			spp = self.taxa.shape[0] - fully_indets

		return (fam, gen, spp)


	def purify(self, taxa2del = None):
		"""
		Discards specific taxa and stems from the plot, typically, herbaceous families.

		Arguments:

		- taxa2del (dict): Dictionary of hierarchical taxa to remove: families ->
		genera -> epithets.

		"""

		taxids = []
		if taxa2del is None:
			taxa2del = {x:None for x in [u'Aizoaceae', u'Alstroemeriaceae', u'Araceae', u'Aristolochiaceae', u'Athyriaceae', u'Blechnaceae', u'Campanulaceae', u'Commelinaceae', u'Cucurbitaceae', u'Cyatheaceae', u'Cyclanthaceae', u'Cyperaceae', u'Dennstaedtiaceae', u'Dicksoniaceae', u'Dryopteridaceae', u'Francoaceae', u'Gesneriaceae', u'Gunneraceae', u'Heliconiaceae', u'Lomariopsidaceae', u'Marantaceae', u'Marcgraviaceae', u'Musaceae', u'Orchidaceae', u'Poaceae', u'Pteridaceae', u'Smilacaceae', u'Strelitziaceae', u'Woodsiaceae', u'Zingiberaceae']}

		for fam in taxa2del:

			if pd.notna(fam):

				if taxa2del[fam] is None:
					taxids += self.taxa[(self.taxa.Family == fam)].index.tolist()

				else:
					for gen in taxa2del[fam]:

						if gen is None:

							taxids += self.taxa[(self.taxa.Family == fam) & self.taxa.Genus.isna()].index.tolist()

						else:

							if taxa2del[fam][gen] is None:

								taxids += self.taxa[(self.taxa.Family == fam) & (self.taxa.Genus == gen)].index.tolist()

							else:

								for epi in taxa2del[fam][gen]:

									if epi is None:

										taxids += self.taxa[(self.taxa.Family == fam) & (self.taxa.Genus == gen) & self.taxa.Epithet.isna()].index.tolist()

									else:

										taxids += self.taxa[(self.taxa.Family == fam) & (self.taxa.Genus == gen) & (self.taxa.Epithet == epi)].index.tolist()

		stemsids = self.stems[self.stems.TaxonID.isin(taxids)].index.tolist()
		self.stems.drop(index = stemsids, inplace = True)
		self.stems.reset_index(drop = True, inplace = True)

		self.taxa.drop(index = taxids, inplace = True)
		self.taxa.reset_index(drop = True, inplace = True)

		return None


	def set_holdridge(self, elevation_raster = None, precipitation_raster = None):
		"""
		Estimates the Holdridge (1966) life zone. Can only be applied to tropical localities.
		"""
		if not self.elevation and self.coordinates:
			self.elevation = allometry.altitude(self.coordinates[0], self.coordinates[1], elevation_raster)

		if not self.precipitation and self.coordinates:
			self.precipitation = allometry.precipitation(self.coordinates[0], self.coordinates[1], precipitation_raster)

		if not self.precipitation or not self.elevation:
			raise ValueError("You need elevation and precipitation values to estimate Holdridge life zone, or the geographic coordinates of the locality.")

		else:
			self.holdridge = allometry.holdridge_col(self.elevation, self.precipitation)

		return None


	def set_chave_forest(self, precipitation_raster = None):
		if not self.precipitation and self.coordinates:
			self.chave_forest = allometry.precipitation(self.coordinates[0], self.coordinates[1], precipitation_raster)

		if not self.precipitation:
			raise ValueError("You need precipitation values to estimate Chave forest type, or the geographic coordinates of the locality.")

		else:
			self.chave_forest = allometry.chaveI_forest(self.precipitation)

		return None


	def set_E(self, chave_E_raster):
		if chave_E_raster:
			self.E = allometry.getE(self.coordinates[0], self.coordinates[1], chave_E_raster)

		else:
			raise ValueError("A raster file with E values is required.")

		return None


	def miss_densi(self):
		"""
		Fill wood density missing entries with the average (by stem frequency)
		wood density in the plot.
		"""
		avewd = 0.0
		avecount = 0

		for tree in self.stems.itertuples():

			thisdens = self.taxa.loc[self.taxa.TaxonID == tree.TaxonID, 'Density'].item()
			if pd.notna(thisdens):
				avewd += thisdens
				avecount += 1

		if avecount > 0:
			avewd /= avecount

		if avewd == 0:
			raise ValueError("Plot average density is zero")

		self.taxa.loc[self.taxa.Density.isna(), 'Density'] = avewd

		return None


	def densities_from_file(self, densities_file):
		"""
		Retrieve wood density from a csv table. If especies or genus is not
		included in the table, the average of the genus or famly is assigned,
		respectively.
		"""
		self.taxa['Density'] = np.nan

		dens = wd.load_data(densities_file)

		def density_updated(row):
			return wd.get_density(row.Family, row.Genus, row.Epithet, dens)

		self.taxa['Density'] = self.taxa.apply(density_updated, axis = 1)

		self.miss_densi()

		return None


	def densities_from_dataframe(self, densities_df):
		"""
		TO TEST
		Retrieve wood density from a csv table. If especies or genus is not
		included in the table, the average of the genus or famly is assigned,
		respectively.
		"""
		self.taxa['Density'] = np.nan
		self.taxa['Density'] = self.taxa.merge(densities_df, on = ['Family','Genus','Epithet'], how = 'left')['Density']
		self.miss_densi()
		return None


	def det_stems(self):
		"""
		Number of stems identified to a taxa with available or inferred density.
		"""
		tax = self.taxa[self.taxa.Density.notna()]['TaxonID'].tolist()
		num = self.stems[self.stems.TaxonID.isin(tax)].shape[0]
		return num


	def biomass(self, method = 'deterministic', equations = ['Chave_II_d'], per_subplot = False):
		"""
		Estimates biomass (ton/ha) from plant community data.

		Arguments:

		- method (string): Method to be employed in calculations.
		"""
		palmid = []
		fernid = []
		if self.det_stems() <= 0:
			raise ValueError("No stems have density values available.")
		
		if 'Arecaceae' in self.taxa.Family.unique():	
			palmid.append(self.taxa.loc[self.taxa.Family == 'Arecaceae', 'TaxonID'].iloc[0].item())
		
		if 'Cyatheaceae' in self.taxa.Family.unique():
			fernid.append(self.taxa.loc[self.taxa.Family == 'Cyatheaceae', 'TaxonID'][0].item())
		elif 'Dicksoniaceae' in self.taxa.Family.unique():
			fernid.append(self.taxa.loc[self.taxa.Family == 'Dicksoniaceae', 'TaxonID'][0].item())
		elif 'Metaxyaceae' in self.taxa.Family.unique():
			fernid.append(self.taxa.loc[self.taxa.Family == 'Metaxyaceae', 'TaxonID'][0].item())
		elif 'Cibotiaceae' in self.taxa.Family.unique():
			fernid.append(self.taxa.loc[self.taxa.Family == 'Cibotiaceae', 'TaxonID'][0].item())
			
		if method == 'deterministic':
			self.alvarez_d = 0.0 # Tons / ha
			self.alvarez_dh = 0.0 # Tons / ha
			self.chave_i = 0.0 # Tons / ha
			self.chave_ii_d = 0.0 # Tons / ha
			self.chave_ii_dh = 0.0 # Tons / ha

			for tree in self.stems.itertuples():
				
				# Move this check to __init__
				if tree.Diameter <= 0:
					if u'StemID' in self.stems.columns:
						print "Stem {0} (StemID) has illegal diameter.".format(tree.StemID)
					else:
						print "Stem {0} (row in self.stems) has illegal diameter.".format(tree.name)

				dens = self.taxa.loc[self.taxa.TaxonID == tree.TaxonID, 'Density'].item()

				#na = self.name
				area = 0
				if self.size_area:
					area = self.size_area[tree.Size]
				elif self.area:
					area = self.area
				else:
					raise ValueError("Plot area has not been set.")

				#try:
				if 'Alvarez_d' in equations and pd.notna(tree.Diameter):
					ta = allometry.alvarez(tree.Diameter, dens, self.holdridge) / area
					
					if 'Subplot' in self.stems.columns:
						self.alvarez_d_sps[tree.Subplot] += ta
					else:
						self.alvarez_d += ta

				if 'Alvarez_dh' in equations and pd.notna(tree.Diameter) and pd.notna(tree.Height):
					if tree.TaxonID in palmid:
						ta = allometry.palm(tree.Height) / area
					elif tree.TaxonID in fernid:
						ta = allometry.fern(tree.Height) / area
					else:
						ta = allometry.alvarez_dh(tree.Diameter, tree.Height, dens, self.holdridge) / area
					
					if 'Subplot' in self.stems.columns:
						self.alvarez_dh_sps[tree.Subplot] += ta
					else:
						self.alvarez_dh += ta

				if 'Chave_II_d' in equations and pd.notna(tree.Diameter):
					ci = allometry.chaveII(tree.Diameter, dens, e_value = float(self.E)) / area
					if 'Subplot' in self.stems.columns:
						self.chave_ii_d_sps[tree.Subplot] += ci
					else:
						self.chave_ii_d += ci

				if 'Chave_II_dh' in equations and pd.notna(tree.Diameter) and pd.notna(tree.Height):
					if tree.TaxonID in palmid:
						cii = allometry.palm(tree.Height) / area
					elif tree.TaxonID in fernid:
						cii = allometry.fern(tree.Height) / area
					else:
						cii = allometry.chaveII_dh(tree.Diameter, tree.Height, dens) / area
					
					if 'Subplot' in self.stems.columns:
						self.chave_ii_dh_sps[tree.Subplot] += cii
					else:
						self.chave_ii_dh += cii

				if 'Chave_I' in equations and pd.notna(tree.Diameter):
					ci = allometry.chaveI(tree.Diameter, dens, self.chave_forest) / area
					if 'Subplot' in self.stems.columns:
						self.chave_i_sps[tree.Subplot] += ci
					else:
						self.chave_i += ci

				"""
				except:
					if u'StemID' in self.stems.columns:
						print "Plot: {0}, StemID: {1}, TaxonID: {2}, Diameter: {3}, Density: {4}, E: {5}".format(self.name, tree.StemID, tree.TaxonID, tree.Diameter, dens, self.E)
					else:
						print "Plot: {0}, Stems row: {1}, TaxonID: {2}, Diameter: {3}, Density: {4}, E: {5}".format(self.name, tree.Index, tree.TaxonID, tree.Diameter, dens, self.E)
				"""
			if len(self.alvarez_dh_sps) > 1:
				self.alvarez_d = sum(self.alvarez_d_sps.values())
				self.alvarez_dh = sum(self.alvarez_dh_sps.values())
				self.chave_i = sum(self.chave_i_sps.values())
				self.chave_ii_d = sum(self.chave_ii_d_sps.values())
				self.chave_ii_dh = sum(self.chave_ii_dh_sps.values())
			
		return None


	def estimate_basal_area(self):

		self.basal_area = 0.0
		
		for tree in self.stems.itertuples():
			if pd.notna(tree.Diameter):
				area = 0
				if self.size_area:
					area = self.size_area[tree.Size]
				elif self.area:
					area = self.area
				else:
					raise ValueError("Plot area has not been set.")

				tba = (((tree.Diameter / 2.0) ** 2) * np.pi) / area
				if 'Subplot' in self.stems.columns:
					self.basal_area_sps[tree.Subplot] += tba
				else:
					self.basal_area += tba

		return None
			
