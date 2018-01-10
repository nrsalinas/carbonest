import pandas as pd
import sqlalchemy as al
import re
import taxon

min_score = 0.95
user = u"root"
password = u"Soledad1"
database = u"Quimera" # u'Quimera' or u'Taxon'
names_included = []
ids_included = []
TNRS_ID = None
bffrlog = ""
logfile = "Quimera_tax_ver_20180110.txt"

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


for row in tax_orphan[[u'Genero',u'Epiteto']].itertuples():
	# Nombres sin Genero no son revisados
	name = None
	gen, epi = u'', u''
	if type(row.Genero) == unicode:
		gen = re.sub(r'\s+', u'', row.Genero)
		if type(row.Epiteto) == unicode:
			epi = re.sub(r'\s+', u'', row.Epiteto)

		name = gen + u" " + epi

	if name:
		try:
			# Verificacion taxonomica
			bffrlog += name
			revised = taxon.otu()
			#revision = taxon.check_names(names, minimum_score = min_score, accepted=True)
			rank = u'sp'
			if epi == u'':
				rank = u'gen'

			# Primer intento de verificacion en tropicos
			trop = taxon.tropicos(name, rank)

			# Segundo intento con tropicos despues de verificacion en tnrs
			if not trop[1]:
				tnrs = taxon.check_names(name)
				newquery = u''
				if tnrs[0][1]:
					newquery = tnrs[0][1].name()
					bits = newquery.split(u' ')
					if len(bits) == 1:
						rank = 'gen'
					elif len(bits) == 2:
						rank = 'sp'
					trop = taxon.tropicos(newquery, rank)

			if trop[1]:
				revised = trop
				bffrlog += ">>>" + revised[1].name() + "\n"

			# La ultima opcion es ipni
			else:
				kew = taxon.ipni(name)
				if kew[1]:
					revised = kew
					bffrlog += ">>>" + revised[1].name() + "\n"

				else:
					# Verificacion manual
					bffrlog += ">>> no encontrado <<<" + "\n"


			####### Falta por actualizar vvvvvv
			if revised[1]:
				# Update record
				already_in_db = False
				dad = int()
				if revised[1].epithet is None:
					if len(tax[(tax.Genero == revised[1].genus) & tax.Epiteto.isna()]):
						dad = int(tax[(tax.Genero == revised[1].genus) & tax.Epiteto.isna()].index[0])
						already_in_db = True
				else:
					if len(tax[(tax.Genero == revised[1].genus) & (tax.Epiteto == revised[1].epithet)]):
						dad = int(tax[(tax.Genero == revised[1].genus) & (tax.Epiteto == revised[1].epithet)].index[0])
						already_in_db = True


				if already_in_db:
					# Name included in db before the execution of current updating routine
					if epi is None:
						mytax = int(tax[(tax.Genero == gen) & tax.Epiteto.isna()].index[0])

					else:
						mytax = int(tax[(tax.Genero == gen) & (tax.Epiteto == epi)].index[0])

					query = u"UPDATE Taxonomia SET SinonimoDe = {0} WHERE TaxonID = {1}".format(dad, mytax)
					ex = conn.execute(query)


				elif revised[1] in names_included:
					# Name included in the db during current update
					dad = ids_included[names_included.index(revised[1])]
					mytax = int()

					if epi == u"":
						mytax = int(tax[(tax.Genero == gen) & tax.Epiteto.isna()].index[0])

					else:
						mytax = int(tax[(tax.Genero == gen) & (tax.Epiteto == epi)].index[0])

					query = u"UPDATE Taxonomia SET SinonimoDe = {0} WHERE TaxonID = {1}".format(dad, mytax)
					ex = conn.execute(query)


				else:
					# New name to db
					names_included.append(revised[1])
					mytax = int()
					if revised[1].epithet is None: # Got only a genus name
						query = u"INSERT INTO Taxonomia (Familia, Genero, AutorGenero, Fuente) " + \
									u"VALUES ('{0}', '{1}', '{2}', {3})".format(revised[1].family,
									revised[1].genus, escape_quote(revised[1].author), TNRS_ID)
					else:
						query = u"INSERT INTO Taxonomia (Familia, Genero, Epiteto, AutorEpiteto, Fuente) " + \
							   u"VALUES ('{0}', '{1}', '{2}', '{3}', {4})".format(revised[1].family,
								revised[1].genus, revised[1].epithet, escape_quote(revised[1].author), TNRS_ID)

					ex = conn.execute(query)
					dad = int(ex.lastrowid)
					ids_included.append(dad)

					if epi == u"":
						mytax = int(tax[(tax.Genero == gen) & tax.Epiteto.isna()].index[0])

					else:
						mytax = int(tax[(tax.Genero == gen) & (tax.Epiteto == epi)].index[0])

					query = u"UPDATE Taxonomia SET SinonimoDe = {0} WHERE TaxonID = {1}".format(dad, mytax)
					ex = conn.execute(query)

		except:
			print "Error with name",name
			continue

	if len(bffrlog) > 5000:
		with open(logfile, "a") as fh:
			fh.write(bffrlog)
		bffrlog = ""

if len(bffrlog):
	with open(logfile, "a") as fh:
		fh.write(bffrlog)
	bffrlog = ""

conn.close()
