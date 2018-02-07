import pandas as pd
import sqlalchemy as al
import pyproj


def acctax(connection):
	"""Adquiere listado de taxa acceptados de la tabla Taxonomia."""

	tax = pd.read_sql_table(table_name='Taxonomia', con = connection)
	acc = {}

	for t in tax.itertuples():
		tax_accepted = int(t.TaxonID)
		dad = t.SinonimoDe
		while pd.notna(dad):
			tax_accepted = int(dad)
			dad = tax[tax.TaxonID == tax_accepted]['SinonimoDe'].item()
		#tax.loc[tax.TaxonID == t.TaxonID, 'TaxonDef' ] = tax_accepted
		fam = tax[tax.TaxonID == tax_accepted]['Familia'].item()
		gen = tax[tax.TaxonID == tax_accepted]['Genero'].item()
		epi = tax[tax.TaxonID == tax_accepted]['Epiteto'].item()
		acc[int(t.TaxonID)] = [fam, gen, epi]
		
	return acc

def dasotab(database, connection, plot, accepted_taxa = False):
	"""
	Produce un Pandas.DataFrame sencillo con la informacion dasometrica y 
	taxonomica de una parcela.
	"""
	
	dtfr = None
	
	query = ''
	
	if accepted_taxa:
		if database == 'Quimera':
			query = 'SELECT TaxonID, Diametro AS Diameter, Altura AS Height FROM Individuos LEFT JOIN Determinaciones ON Dets=DetID LEFT JOIN Taxonomia ON Taxon=TaxonID WHERE Plot = {0}'.format(plot)
			
		elif database == 'IFN':
			query = "SELECT TaxonID, DiametroP AS Diameter, AlturaTotal AS Height, TalloID AS StemID, Tamano AS Size, Subparcela as Subplot FROM Tallos LEFT JOIN Individuos ON Individuo = IndividuoID LEFT JOIN Determinaciones ON Dets = DetID LEFT JOIN Taxonomia ON Taxon = TaxonID LEFT JOIN Conglomerados on Plot = PlotID WHERE Dets IS NOT NULL AND Tamano IN ('L', 'F', 'FG') AND PlotID = {0}".format(plot)
		
		dtfr = pd.read_sql_query(sql = query, con = connection)
		
		dtfr['Family'] = dtfr.apply(lambda x: accepted_taxa[x.TaxonID][0], axis = 1)
		dtfr['Genus'] = dtfr.apply(lambda x: accepted_taxa[x.TaxonID][1], axis = 1)
		dtfr['Epithet'] = dtfr.apply(lambda x: accepted_taxa[x.TaxonID][2], axis = 1)
		dtfr.drop(columns='TaxonID', inplace=True)
		
		
	else:
		if database == 'Quimera':
			query = 'SELECT Familia AS Family, Genero AS Genus, Epiteto AS Epithet, Diametro AS Diameter, Altura AS Height FROM Individuos LEFT JOIN Determinaciones ON Dets=DetID LEFT JOIN Taxonomia ON Taxon=TaxonID WHERE Plot = {0}'.format(plot)
			
		elif database == 'IFN':
			query = "SELECT Familia AS Family, Genero AS Genus, Epiteto AS Epithet, DiametroP AS Diameter, AlturaTotal AS Height, TalloID AS StemID, Tamano AS Size, Subparcela as Subplot FROM Tallos LEFT JOIN Individuos ON Individuo = IndividuoID LEFT JOIN Determinaciones ON Dets = DetID LEFT JOIN Taxonomia ON Taxon = TaxonID LEFT JOIN Conglomerados on Plot = PlotID WHERE Dets IS NOT NULL AND Tamano IN ('L', 'F', 'FG') AND PlotID = {0}".format(plot)
			
		dtfr = pd.read_sql_query(sql = query, con = connection)
	
	return dtfr


def coords(database, connection, plot, subplot = None):
	"""
	Consulta las coordenadas geograficas de una parcela o conglomerado.
	"""
	mycoords = (None, None)
	
	if database == 'Quimera':

		# WGS 84 zone 18 N projection
		inpr = pyproj.Proj('+proj=utm +zone=18 +ellps=WGS84 +datum=WGS84 +units=m +no_defs')
		# WGS 84 projection
		outpr = pyproj.Proj(init='epsg:4326')
		
		query = 'SELECT X,Y FROM Parcelas WHERE PlotID = {0}'.format(plot)
		point = pd.read_sql_query(sql = query, con = connection)

		mycoords = pyproj.transform(inpr, outpr, point.X[0], point.Y[0])

	elif database == 'IFN':

		query = 'SELECT Longitud, Latitud FROM Conglomerados LEFT JOIN Coordenadas ON Plot = PlotID WHERE PlotID = {0} AND SPF = 1'.format(plot)
		
		point = pd.read_sql_query(sql = query, con = connection)
		
		mycoords = point.Longitud[0], point.Latitud[0]

	return mycoords
	
