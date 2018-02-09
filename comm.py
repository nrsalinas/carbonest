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
	values the sampling area (ha) of the category (float).
	
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
			
			self.holdridge = None
			self.chave_forest = None
			
			self.E = None
			self.elevation = None
			self.precipitation = None
			
			self.size_def = None
			self.size_area = None # Effective sampled area per diametric class
			self.area = None # Total area
			
			self.alvarez = 0.0 # Tons / ha
			self.chave_i = 0.0 # Tons / ha
			self.chave_ii = 0.0 # Tons / ha
			
			
			# optional fields
			fields = ['Diameter','Height','TaxonID']
			if 'Subplot' in dataframe.columns:
				fields.append('Subplot')
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
			

	def purify(self, taxa2del = None):
		"""
		Discards specific taxa from the plot, typically, herbaceous families.
		
		Arguments:
		
		- taxa2del (dict): Dictionary of hierarchical taxa to remove: families ->
		genera -> epithets.
		
		"""
		taxids = []
		if taxa2del is None:
			taxa2del = {x:None for x in [u'Aizoaceae', u'Alstroemeriaceae', u'Araceae', u'Aristolochiaceae', u'Athyriaceae', u'Blechnaceae', u'Campanulaceae', u'Commelinaceae', u'Cucurbitaceae', u'Cyatheaceae', u'Cyclanthaceae', u'Cyperaceae', u'Dennstaedtiaceae', u'Dicksoniaceae', u'Dryopteridaceae', u'Francoaceae', u'Gesneriaceae', u'Gunneraceae', u'Heliconiaceae', u'Lomariopsidaceae', u'Marantaceae', u'Marcgraviaceae', u'Musaceae', u'Orchidaceae', u'Poaceae', u'Pteridaceae', u'Smilacaceae', u'Strelitziaceae', u'Woodsiaceae', u'Zingiberaceae']}
		
		for fam in taxa2del:
			
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

	
	def biomass(self, method = 'deterministic'):
		"""
		Estimates biomass (ton/ha) from plant community data.
		
		Arguments:
		
		- method (string): Method to be employed in calculations. Options are
		`deterministic` (traditional method), `montecarlo` (simulate uncertainty
		following the proposal by Chave et al.), and `bayes` (full bayesian 
		estimate proposed by IDEAM-SMByC).
		"""
		if self.det_stems() <= 0:
			raise ValueError("No stems have density values available.")
			
		if method == 'deterministic':
			self.alvarez = 0.0 # Tons / ha
			self.chave_i = 0.0 # Tons / ha
			self.chave_ii = 0.0 # Tons / ha

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
					
				try:
					self.alvarez += allometry.alvarez(tree.Diameter, dens, self.holdridge) / area
					self.chave_ii += allometry.chaveII(tree.Diameter, dens, e_value = float(self.E)) / area
					self.chave_i += allometry.chaveI(tree.Diameter, dens, self.chave_forest) / area
			
				except:
					if u'StemID' in self.stems.columns:
						print "Plot: {0}, StemID: {1}, TaxonID: {2}, Diameter: {3}, Density: {4}, E: {5}".format(self.name, tree.StemID, tree.TaxonID, tree.Diameter, dens, self.E)
					else:
						print "Plot: {0}, Stems row: {1}, TaxonID: {2}, Diameter: {3}, Density: {4}, E: {5}".format(self.name, tree.Index, tree.TaxonID, tree.Diameter, dens, self.E)

		return None
		
		