#
# Nombres validos son sinomimos de si mismos
#

import pandas as pd
import sqlalchemy as al
import re
import taxon
import codecs

min_score = 0.90
user = u"root"
password = u"Soledad1"
database = u'IFN_2018' # u'Quimera' | u'IFN' | u'IFN_2018'
names_included = []
ids_included = []
TNRS_ID = None
Tropicos_ID = None
IPNI_ID = None
bffrlog = ""
logfile = "IFN_2018_tax_ver_20180516.txt"

def escape_quote(autor):
	out = None
	if isinstance(autor, unicode):
		out = autor.replace(u"'", u"\\'")
	return out

engine = al.create_engine(
	'mysql+mysqldb://{0}:{1}@localhost/{2}?charset=utf8&use_unicode=1&unix_socket=/var/run/mysqld/mysqld.sock'.format(
	user, password, database), encoding='utf-8')

conn = engine.connect()

##################################
# Fuentes de autoridad taxonomica
##################################

query = u"SELECT FuenteID FROM Fuentes WHERE Acronimo = 'TNRS' AND YEAR = 2018"
ex = conn.execute(query)
if ex.rowcount > 0:
	TNRS_ID = int(ex.fetchone()[u'FuenteID'])
else:
	query = u"INSERT INTO Fuentes (Nombre, Acronimo, Year, Url) VALUES ('Taxonomic Name Resolution Service', 'TNRS', 2018, 'http://tnrs.iplantc.org')"
	ex = conn.execute(query)
	TNRS_ID = int(ex.lastrowid)

query = u"SELECT FuenteID FROM Fuentes WHERE Acronimo = 'Tropicos' AND YEAR = 2018"
ex = conn.execute(query)
if ex.rowcount > 0:
	TNRS_ID = int(ex.fetchone()[u'FuenteID'])
else:
	query = u"INSERT INTO Fuentes (Nombre, Acronimo, Year, Url) VALUES ('Tropicos', 'TROPICOS', 2018, 'http://www.tropicos.org/')"
	ex = conn.execute(query)
	Tropicos_ID = int(ex.lastrowid)


query = u"SELECT FuenteID FROM Fuentes WHERE Acronimo = 'IPNI' AND YEAR = 2018"
ex = conn.execute(query)
if ex.rowcount > 0:
	TNRS_ID = int(ex.fetchone()[u'FuenteID'])
else:
	query = u"INSERT INTO Fuentes (Nombre, Acronimo, Year, Url) VALUES ('The International Plant Name Index', 'IPNI', 2018, 'http://www.ipni.org/')"
	ex = conn.execute(query)
	IPNI_ID = int(ex.lastrowid)


tax = pd.read_sql_table(table_name='Taxonomia',con=conn, index_col='TaxonID')

tax_orphan = tax[tax.SinonimoDe.isna()].sort_values([u'Familia', u'Genero',u'Epiteto'])

names = u""


for row in tax_orphan[[u'Genero',u'Epiteto']].itertuples():
	# Nombres sin Genero no son revisados
	print row.Genero, row.Epiteto
	name = None
	aut = None # Autoridad taxonomica
	gen, epi = u'', u''
	if type(row.Genero) == unicode:
		gen = re.sub(r'\s+', u'', row.Genero)
		if type(row.Epiteto) == unicode:
			epi = re.sub(r'\s+', u'', row.Epiteto)
			name = gen + u' ' + epi
		else:
			name = gen

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
				tnrs = taxon.check_names(name, minimum_score = min_score)
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
				aut = Tropicos_ID
				revised = trop
				bffrlog += ">>>" + revised[1].name() + "\n"

			# La ultima opcion es ipni
			else:
				kew = taxon.ipni(name)
				if kew[1]:
					Aut = IPNI_ID
					revised = kew
					bffrlog += ">>>" + revised[1].name() + "\n"

				else:
					# Verificacion manual
					bffrlog += ">>> no encontrado <<<" + "\n"


			####### Falta por actualizar #########
			if revised[1] and revised[1].genus == gen and revised[0].epithet == epi:
				# No changes, but try to update authors
				
				if pd.notna(revised[1].author):
					
					if pd.isna(epi) or epi == u'':
						mytax = int(tax[(tax.Genero == gen) & tax.Epiteto.isna()].index[0])

					else:
						mytax = int(tax[(tax.Genero == gen) & (tax.Epiteto == epi)].index[0])
					
					if aut:
						query = u"UPDATE Taxonomia SET Autor = '{0}', Fuente = {1} WHERE TaxonID = {2}".format(revised[1].author, aut, mytax)
					else:
						query = u"UPDATE Taxonomia SET Autor = '{0}' WHERE TaxonID = {1}".format(revised[1].author, mytax)
						
					
					ex = conn.execute(query)
				
			
			elif revised[1]:
				# Update record
				already_in_db = False
				dad = int()
				if pd.isna(revised[1].epithet):
					if len(tax[(tax.Genero == revised[1].genus) & tax.Epiteto.isna()]):
						dad = int(tax[(tax.Genero == revised[1].genus) & tax.Epiteto.isna()].index[0])
						already_in_db = True
				else:
					if len(tax[(tax.Genero == revised[1].genus) & (tax.Epiteto == revised[1].epithet)]):
						dad = int(tax[(tax.Genero == revised[1].genus) & (tax.Epiteto == revised[1].epithet)].index[0])
						already_in_db = True


				if already_in_db:
					# Name included in db before the execution of current updating routine
					if pd.isna(epi) or epi == u'':
						mytax = int(tax[(tax.Genero == gen) & tax.Epiteto.isna()].index[0])

					else:
						mytax = int(tax[(tax.Genero == gen) & (tax.Epiteto == epi)].index[0])
					
					if aut:
						query = u"UPDATE Taxonomia SET SinonimoDe = {0}, Fuente = {1} WHERE TaxonID = {2}".format(dad, aut, mytax)
					else:
						query = u"UPDATE Taxonomia SET SinonimoDe = {0}, Fuente = NULL WHERE TaxonID = {1}".format(dad, mytax)
					ex = conn.execute(query)
					
					# Include author
					if len(revised[1].author) > 1:
						if aut:
							query = u"UPDATE Taxonomia SET Autor = '{0}', Fuente = {1} WHERE TaxonID = {2}".format(revised[1].author, aut, dad)
						else:
							query = u"UPDATE Taxonomia SET Autor = '{0}', Fuente = NULL WHERE TaxonID = {1}".format(revised[1].author, dad)
						ex = conn.execute(query)


				elif revised[1] in names_included:
					# Name included in the db during current update
					dad = ids_included[names_included.index(revised[1])]
					mytax = int()

					if epi == u"":
						mytax = int(tax[(tax.Genero == gen) & tax.Epiteto.isna()].index[0])

					else:
						mytax = int(tax[(tax.Genero == gen) & (tax.Epiteto == epi)].index[0])

					if aut:
						query = u"UPDATE Taxonomia SET SinonimoDe = {0}, Fuente = {1} WHERE TaxonID = {2}".format(dad, aut, mytax)
					else:
						query = u"UPDATE Taxonomia SET SinonimoDe = {0}, Fuente = NULL WHERE TaxonID = {1}".format(dad, mytax)
					ex = conn.execute(query)


				else:
					# New name to db
					names_included.append(revised[1])
					mytax = int()
					if revised[1].epithet is None: # Got only a genus name
						if aut:
							query = u"INSERT INTO Taxonomia (Familia, Genero, Autor, Fuente) " + \
									u"VALUES ('{0}', '{1}', '{2}', {3})".format(revised[1].family,
									revised[1].genus, escape_quote(revised[1].author), aut)
						else:
							query = u"INSERT INTO Taxonomia (Familia, Genero, Autor, Fuente) " + \
									u"VALUES ('{0}', '{1}', '{2}', NULL)".format(revised[1].family,
									revised[1].genus, escape_quote(revised[1].author))
					else:
						if aut:
							query = u"INSERT INTO Taxonomia (Familia, Genero, Epiteto, Autor, Fuente) " + \
							   u"VALUES ('{0}', '{1}', '{2}', '{3}', {4})".format(revised[1].family,
								revised[1].genus, revised[1].epithet, escape_quote(revised[1].author), aut)
						else:
							query = u"INSERT INTO Taxonomia (Familia, Genero, Epiteto, Autor, Fuente) " + \
							   u"VALUES ('{0}', '{1}', '{2}', '{3}', NULL)".format(revised[1].family,
								revised[1].genus, revised[1].epithet, escape_quote(revised[1].author))
								
					ex = conn.execute(query)
					dad = int(ex.lastrowid)
					ids_included.append(dad)

					if epi == u"":
						mytax = int(tax[(tax.Genero == gen) & tax.Epiteto.isna()].index[0])

					else:
						mytax = int(tax[(tax.Genero == gen) & (tax.Epiteto == epi)].index[0])

					if aut:
						query = u"UPDATE Taxonomia SET SinonimoDe = {0}, Fuente = {1} WHERE TaxonID = {2}".format(dad, aut, mytax)
					else:
						query = u"UPDATE Taxonomia SET SinonimoDe = {0}, Fuente = NULL WHERE TaxonID = {1}".format(dad, mytax)
					ex = conn.execute(query)
					

		except:
			bffrlog += ">>> Problema con nombre {0} <<<\n".format(name)
			continue

	if len(bffrlog) > 5000:
		with codecs.open(logfile, "a", encoding='utf8') as fh:
			fh.write(bffrlog)
		bffrlog = ""

if len(bffrlog):
	with codecs.open(logfile, "a", encoding='utf8') as fh:
		fh.write(bffrlog)
	bffrlog = ""

conn.close()
