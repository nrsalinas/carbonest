import pandas as pd
import sqlalchemy as al
import re
import taxon

min_score = 0.95
user = u""
password = u""
database = u"Quimera" # u'Quimera' or u'Taxon'
names_included = []
ids_included = []
TNRS_ID = None

def escape_quote(autor):
	out = None
	if isinstance(autor, unicode):
		out = autor.replace(u"'", u"\\'")
	return out

engine = al.create_engine(
	'mysql+mysqldb://{0}:{1}@localhost/{2}?charset=utf8&use_unicode=1'.format(
	user, password, database), encoding='utf-8')

conn = engine.connect()

query = u"SELECT FuenteID FROM Fuentes WHERE Acronimo = 'TNRS' AND YEAR = 2018"
ex = conn.execute(query)
if ex.rowcount > 0:
	TNRS_ID = int(ex.fetchone()[u'FuenteID'])
else:
	query = u"INSERT INTO Fuentes (Nombre, Acronimo, Year, Url) VALUES ('Taxonomic Name Resolution Service', 'TNRS', 2018, 'http://tnrs.iplantc.org')"
	ex = conn.execute(query)
	TNRS_ID = int(ex.lastrowid)

tax = pd.read_sql_table(table_name='Taxonomia',con=conn, index_col='TaxonID')

tax_orphan = tax[tax.SinonimoDe.isna()]

names = u""


for s in xrange(0, tax_orphan.shape[0], 400):
	names = u""
	e = int()
	if (s + 400) < tax_orphan.shape[0]:
		e = s + 400
	else:
		e = tax_orphan.shape[0]


	for row in tax_orphan[s:e][[u'Genero',u'Epiteto']].itertuples():
		# Nombres son Genero no son revisados
		if type(row.Genero) == unicode:
			gen = re.sub(r'\s+', u'', row.Genero)
			if type(row.Epiteto) == unicode:
				epi = re.sub(r'\s+', u'', row.Epiteto)
				names += u"{0}%20{1},".format(gen, epi)
			else:
				names += u"{0},".format(gen)

	names = names.rstrip(u',')
	revision = taxon.check_names(names, minimum_score = min_score, accepted=True)

	for rev in revision:
		# Report to log file
		if rev[u"resp"][u"score"] < min_score:
			print ">>>>>> Not update (score {0}): {1} {2}.".format(rev[u"resp"][u"score"],
				rev[u"query"][u"genus"], rev[u"query"][u"epithet"])

		elif rev[u"query"][u"genus"] == rev[u"resp"][u"genus"] and \
			rev[u"query"][u"epithet"] == rev[u"resp"][u"epithet"]:

			print ">>>>>> Not update (Name OK): {1} {2}.".format(rev[u"resp"][u"score"],
				rev[u"query"][u"genus"], rev[u"query"][u"epithet"])

		# Update record
		else:

			already_in_db = False
			dad = int()
			if rev[u"resp"][u"epithet"] is None:
				if len(tax[(tax.Genero == rev[u"resp"][u"genus"]) & tax.Epiteto.isna()]):
					dad = int(tax[(tax.Genero == rev[u"resp"][u"genus"]) & tax.Epiteto.isna()].index[0])
					already_in_db = True
			else:
				if len(tax[(tax.Genero == rev[u"resp"][u"genus"]) & (tax.Epiteto == rev[u"resp"][u"epithet"])]):
					dad = int(tax[(tax.Genero == rev[u"resp"][u"genus"]) & (tax.Epiteto == rev[u"resp"][u"epithet"])].index[0])
					already_in_db = True


			if already_in_db:
				# Name included in db before the execution of current updating routine
				if rev[u"query"][u"epithet"] is None:
					mytax = int(tax[(tax.Genero == rev[u"query"][u"genus"]) & tax.Epiteto.isna()].index[0])

				else:
					mytax = int(tax[(tax.Genero == rev[u"query"][u"genus"]) & (tax.Epiteto == rev[u"query"][u"epithet"])].index[0])

				query = u"UPDATE Taxonomia SET SinonimoDe = {0} WHERE TaxonID = {1}".format(dad, mytax)
				ex = conn.execute(query)


			elif rev[u"resp"] in names_included:
				# Name included in the db during current update
				dad = ids_included[names_included.index(rev[u"resp"])]
				mytax = int()

				if rev[u"query"][u"epithet"] is None:
					mytax = int(tax[(tax.Genero == rev[u"query"][u"genus"]) & tax.Epiteto.isna()].index[0])

				else:
					mytax = int(tax[(tax.Genero == rev[u"query"][u"genus"]) & (tax.Epiteto == rev[u"query"][u"epithet"])].index[0])

				query = u"UPDATE Taxonomia SET SinonimoDe = {0} WHERE TaxonID = {1}".format(dad, mytax)
				ex = conn.execute(query)


			else:
				# New name to db
				names_included.append(rev[u"resp"])
				mytax = int()
				if rev[u"resp"][u"epithet"] is None: # Got only a genus name
					query = u"INSERT INTO Taxonomia (Familia, Genero, AutorGenero, Fuente) " + \
								u"VALUES ('{0}', '{1}', '{2}', {3})".format(rev[u"resp"][u"family"],
								rev[u"resp"][u"genus"], escape_quote(rev[u"resp"][u"author"]), TNRS_ID)
				else:
					query = u"INSERT INTO Taxonomia (Familia, Genero, Epiteto, AutorEpiteto, Fuente) " + \
						   u"VALUES ('{0}', '{1}', '{2}', '{3}', {4})".format(rev[u"resp"][u"family"],
							rev[u"resp"][u"genus"], rev[u"resp"][u"epithet"], escape_quote(rev[u"resp"][u"author"]), TNRS_ID)

				ex = conn.execute(query)
				dad = int(ex.lastrowid)
				ids_included.append(dad)

				if rev[u"query"][u"epithet"] is None:
					mytax = int(tax[(tax.Genero == rev[u"query"][u"genus"]) & tax.Epiteto.isna()].index[0])

				else:
					mytax = int(tax[(tax.Genero == rev[u"query"][u"genus"]) & (tax.Epiteto == rev[u"query"][u"epithet"])].index[0])

				query = u"UPDATE Taxonomia SET SinonimoDe = {0} WHERE TaxonID = {1}".format(dad, mytax)
				ex = conn.execute(query)

		print "\n"

conn.close()
