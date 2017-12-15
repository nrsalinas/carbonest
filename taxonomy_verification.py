import pandas as pd
import sqlalchemy as sqal
import re
import taxon

user = u""
password = u""
database = u"" # u'Quimera' or u'Taxon'

engine = sqal.create_engine(
	'mysql+mysqldb://{0}:{1}@localhost/{2}?charset=utf8&use_unicode=1'.format(
	user, password, database), encoding='utf-8')

conn = engine.connect()

tax = pd.read_sql_table(table_name='Taxonomia',con=engine, index_col='TaxonID')

names = u""
for s in xrange(0, tax.shape[0], 400):
	names = u""
	e = int()
	if (s + 400) < tax.shape[0]:
		e = s + 400
	else:
		e = tax.shape[0]

	for row in tax[s:e][[u'Genero',u'Epiteto']].itertuples():
		# Nombres son Genero no son revisados
		if type(row.Genero) == unicode:
			gen = re.sub(r'\s+', u'', row.Genero)
			if type(row.Epiteto) == unicode:
				epi = re.sub(r'\s+', u'', row.Epiteto)
				names += u"{0}%20{1},".format(gen, epi)
			else:
				names += u"{0},".format(gen)

	names = names.rstrip(u',')
	revision = taxon.check_names(names, accepted=True)

	for rev in revision:
		#if len(tax[(tax.Genero == rev[0]) & (tax.Epiteto == rev[1])]) > 0:
		#new_name = u" ".join(filter(lambda x: isinstance(x, unicode), rev[0:2]))
		if rev[:4] != rev[-4:] and not rev[:5] in names_to_include:
			names_to_include.append(rev[:5])
			if rev[1] is None: # Genus name
				query = u"INSERT INTO Taxonomia (Genero, AutorGenero, Fuente) VALUES ({0}, {1}, ####,)".format(rev[0], rev[4])
				ex = conn.execute(query)
				dad = ex.lastrowid

				query = u"SELECT TaxonID FROM Taxonomia WHERE Genero = {0} AND Epiteto = {1})".format(rev[-4], rev[-3])
				ex = conn.execute(query)

				query = u"UPDATE Taxonomia SET SinonimoDe = {0} WHERE TaxonID = {1}".format(dad, ex)
				ex = conn.execute(query)

			else: #binomial
				query = u"INSERT INTO Taxonomia (Genero, Epiteto, AutorEpiteto, Fuente) VALUES ({0}, {1}, {2}, ####,)".format(rev[0], rev[1], rev[4])
				ex = conn.execute(query)
				dad = ex.lastrowid

				query = u"SELECT TaxonID FROM Taxonomia WHERE Genero = {0} AND Epiteto = {1})".format(rev[-4], rev[-3])
				ex = conn.execute(query)

				query = u"UPDATE Taxonomia SET SinonimoDe = {0} WHERE TaxonID = {1}".format(dad, ex)
				ex = conn.execute(query)

"""
Plan
1. Retrieve all names (genus, epithet, author) from the database.

2. Query TNRS in batches of 500, retrieve only genus, epithet, author

3. For each retrieved name:

	a. Check if it is equal to the corresponding queried name

	b. If they are different because of the spelling:

		i. If the new spelling is already in database: update Taxonomi by adding a synonym

		ii. If the new spelling is absent in db then insert a new row and add synonym

	c. If they are different because of different values:

		i. If the new value is already in database: update Taxonomy by adding a synonym

		ii. If the new value is absent in db then insert a new row and add synonym




"""
