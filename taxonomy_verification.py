import pandas as pd
import sqlalchemy as al
import re
import taxon

user = u""
password = u""
database = u"" # u'Quimera' or u'Taxon'

engine = al.create_engine(
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

		if (rev[u"query"][u"genus"] != rev[u"resp"][u"genus"] or
			rev[u"query"][u"epithet"] != rev[u"resp"][u"epithet"]):

			if rev[u"resp"] in names_included:
				dad = ids_included[names_included.index(rev[u"resp"])]

				if rev[u"query"][u"epithet"] is None:
					query = u"SELECT TaxonID FROM Taxonomia WHERE Genero = '{0}' AND Epiteto IS NULL".format(
								rev[u"query"][u"genus"])
				else:
					query = u"SELECT TaxonID FROM Taxonomia WHERE Genero = '{0}' AND Epiteto = '{1}'".format(
								rev[u"query"][u"genus"], rev[u"query"][u"epithet"])

				ex = conn.execute(query)
				mytax = int(ex.fetchone()[u'TaxonID'])

				query = u"UPDATE Taxonomia SET SinonimoDe = {0} WHERE TaxonID = {1}".format(dad, mytax)

				ex = conn.execute(query)

			else:
				names_included.append(rev[u"resp"])
				if rev[u"resp"][u"epithet"] is None: # Got only a genus name
					query = u"INSERT INTO Taxonomia (Familia, Genero, AutorGenero, Fuente) " + \
								u"VALUES ('{0}', '{1}', '{2}', 'TNRS')".format(rev[u"resp"][u"family"],
								rev[u"resp"][u"genus"], rev[u"resp"][u"author"])
				else:
					query = u"INSERT INTO Taxonomia (Familia, Genero, Epiteto, AutorEpiteto, Fuente) " + \
						   u"VALUES ('{0}', '{1}', '{2}', 'TNRS')".format(rev[u"resp"][u"family"],
							rev[u"resp"][u"genus"], rev[u"resp"][u"epithet"], rev[u"resp"][u"author"])

				ex = conn.execute(query)
				dad = int(ex.lastrowid)
				ids_included.append(dad)

				if rev[u"query"][u"epithet"] is None:
					query = u"SELECT TaxonID FROM Taxonomia WHERE Genero = '{0}' AND Epiteto IS NULL".format(
								rev[u"query"][u"genus"])
				else:
					query = u"SELECT TaxonID FROM Taxonomia WHERE Genero = '{0}' AND Epiteto = '{1}'".format(
								rev[u"query"][u"genus"], rev[u"query"][u"epithet"])

				ex = conn.execute(query)
				mytax = int(ex.fetchone()[u'TaxonID'])

				query = u"UPDATE Taxonomia SET SinonimoDe = {0} WHERE TaxonID = {1}".format(dad, mytax)

				ex = conn.execute(query)

conn.close()
