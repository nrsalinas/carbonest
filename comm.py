import pandas as pd

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
		
		The following columns are optional:

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
		
		if not csv_file and not dbconn:
			raise ValueError("Plot could not be instantiated: no data was parse.")

		elif csv_file:
			pass
			
		elif pd_dtfr and isinstance(dataframe, pd.dataframe):
			
			# scalars
			self.coordinates = None
			self.holdridge = None
			self.chave_forest = None
			self.E = None
			self.elevation = None
			
					
			self.taxa # accepted taxonomic names
			self.stems # tree data
		
	
