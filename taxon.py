import urllib2
import json
import re

class otu(object):
	
	def __init__(self):
		self.family = None
		self.genus = None
		self.epithet = None
		self.infraRank = None
		self.infraEpithet = None
		self.author = None
		self.year = None

	def name(self, author = False):
		out = u""
		if self.genus and isinstance(self.genus, unicode):
			if self.epithet and isinstance(self.epithet, unicode):
				if self.infraRank and self.infraEpithet and isinstance(self.infraRank, unicode) and isinstance(self.infraEpithet, unicode):
					out = self.genus + u" " + self.epithet + u" " + self.infraRank + u" " + self.infraEpithet
				else:
					out = self.genus + u" " + self.epithet
			else:
				out = self.genus
		elif self.family and isinstance(self.family, unicode):
			out = self.family
		if author and isinstance(self.author, unicode):
			out += u" " + self.author
		return out

	def binomial(self):
		out = u""
		if self.genus and self.epithet and isinstance(self.genus, unicode) and isinstance(self.epithet, unicode):
			out += self.genus + u" " + self.epithet
		return out

	def from_string(self, taxon_name):
		"""
		Splits a taxonomic name into its components: genus, specific epithet,
		infraspecific rank, and infraspecific epithet. Returns a dictionary.
		"""
		if isinstance(taxon_name, str):
			taxon_name = taxon_name.decode('utf-8')
		if isinstance(taxon_name, unicode):
			bits = taxon_name.split(u' ')
			if len(bits):
				self.genus = bits[0]
				if len(bits) > 1:
					self.epithet = bits[1]
					if len(bits) > 2:
						if bits[2] in [u'var.', u'spp.', u'f.']:
							self.infraRank = bits[2]
							self.infraEpithet = bits[3]
							if len(bits) > 4:
								self.author = u' '.join(bits[4:])
						else:
							self.author = u' '.join(bits[2:])
		return None


def url_space(taxon_name):
	"""Replaces text spaces with url-encoded spaces."""
	new_name = u""
	if isinstance(taxon_name, str):
		new_name = taxon_name.replace(" ","%20")
	elif isinstance(taxon_name, unicode):
		new_name = taxon_name.replace(u" ",u"%20")
	else:
		new_name = None
	return new_name

def split_name(taxon_name):
	"""
	Splits a taxonomic name into its components: genus, specific epithet,
	infraspecific rank, and infraspecific epithet. Returns a dictionary.
	"""
	out = {
		u"family" : None,
		u"genus" : None,
		u"epithet" : None,
		u"infraRank" : None,
		u"infraEpithet" : None,
		u"author" : None
		}

	if isinstance(taxon_name, str):
		taxon_name = taxon_name.decode('utf-8')
	if isinstance(taxon_name, unicode):
		bits = taxon_name.split(u' ')
		if len(bits):
			out[u"genus"] = bits[0]
			if len(bits) > 1:
				out[u"epithet"] = bits[1]
				if len(bits) == 4:
					out[u"infraRank"] = bits[2]
					out[u"infraEpithet"] = bits[3]
	return out


def tnrs(names, minimum_score = 0.95 ,
		tnrs_url = u"http://tnrs.iplantc.org/tnrsm-svc/matchNames" ,
		resLevel=u"best", accepted = False):
	"""
	Parses name queries to the Taxonomic Name Resolution Service
	(http://tnrs.iplantcollaborative.org) and retrives a corrected taxonomic
	name. Outputs a list of tuples: one per each taxon in the query. Each tuple
	contains the correct genus, specific epithet, infraspecific rank,
	infraspecific epithet, and author. Their value will be None if not retrieved.

	Arguments:

	- names (str, unicode, or list): Should not include authors.

	- minimum_score (float): Minimum TNRS score to be accepted as a match.

	- tnrs_url (unicode): URL address of the service.

	- resLevel (u"best or u"all"): Resolution level expected in the result, `best`
	only keeps the best name match, `all` saves all the matches.

	- accepted (boolean): Checks the taxonomically accepted name. If `False` only
	asserts the spelling of the name(s) in the query.

	"""

	checked = []

	if isinstance(names, list) or isinstance(names, tuple):
		if isinstance(names[0], str):
			names = u",".join(map(lambda x: url_space(x).decode('utf-8'), names))
		elif isinstance(names[0], unicode):
			names = u",".join(map(lambda x: url_space(x), names))
	elif isinstance(names, str):
		names = url_space(names).decode('utf-8')
	elif isinstance(names, unicode):
		names = url_space(names)
	else:
		checked = None ### Throw TypeError

	query = u"{0}?retrieve={1}&names={2}".format(tnrs_url, resLevel, names)

	req = urllib2.Request(query)
	resp = urllib2.urlopen(req)
	result = json.loads(resp.read())

	#print result

	for nami in result[u'items']:
		out = (otu(), otu())

		# get a dict similar to out[u"resp"] for the queried name
		out[0].from_string(nami[u'nameSubmitted'])

		if nami[u'scientificScore'] or nami[u'genusScore']:
			nami[u'scientificScore'] = float(nami[u'scientificScore'])
			nami[u'genusScore'] = float(nami[u'genusScore'])
			#out[u"resp"][u"score"] = nami[u'scientificScore']

			if nami[u'scientificScore'] >= minimum_score or nami[u'genusScore'] == 1: # Correct name in nami[nameScientific]

				if nami[u'family']:
					out[1].family = nami[u'family']

				if accepted and nami[u'acceptedName']:
					out[1].from_string(nami[u'acceptedName'])
					out[1].author = nami[u'acceptedAuthor']

				else:
					if nami[u'genusScore'] > minimum_score:
						#nami[u'genusScore'] = float(nami[u'genusScore'])
						out[1].genus = nami[u'genus']
						out[1].family = nami[u'family']

						if nami[u'epithetScore']:
							nami[u'epithetScore'] = float(nami[u'epithetScore'])
							if nami[u'epithetScore'] > minimum_score:
								out[1].epithet = nami[u'epithet']

							if nami[u'infraspecific1EpithetScore']:
								nami[u'infraspecific1EpithetScore'] = float(nami[u'infraspecific1EpithetScore'])
								if nami[u'infraspecific1EpithetScore'] > minimum_score:
									out[1].infraEpithet = nami[u'infraspecific1Epithet']
									if nami[u'nameScientific'].find(u' var. ') >= 0:
										out[1].infraRank =  u"var."
									elif nami[u'nameScientific'].find(u' subsp. ') >= 0:
										out[1].infraRank =  u"subsp."

						# authorAttributed always retrieved
						if nami[u'authorAttributed']:
							out[1].author = nami[u'authorAttributed']

		checked.append(out)

	return checked

def extract_year(tropicos_string):
	out = None
	bits = re.split(r'\s+', tropicos_string)
	bits = map(lambda x: re.sub(r'\D','',x), bits)
	bits = filter(lambda x: len(x) >= 4, bits)

	topop = []
	toadd = []
	for ind,b in enumerate(bits):
		if len(b) == 8:
			toadd += b[:4] + b[4:]
			topop.append(b)
	bits = filter(lambda x: x not in topop, bits)
	bits += toadd

	if len(bits):
		bits = map(int, bits)
		bits = sorted(bits, reverse = True)
		out = bits[0]
		#if bits[0] > 2017:
		#	print "\nLiterature from the future:", bits[0]

	return out

def tropicos(name, rank, file_api_key = "tropicos_api_key"):
	"""
	rank : `sp` or `gen`.
	"""
	api_key = ''
	with open(file_api_key, 'r') as fh:
		api_key = fh.read()
	api_key = api_key.rstrip().decode('utf8')

	service = u"http://services.tropicos.org/"

	if isinstance(name, str):
		name = name.decode('utf8')

	if not isinstance(name, unicode):
		raise TypeError("Query should be a string or unicode.")

	in_name = otu()
	in_name.from_string(name)
	url_name = url_space(name)
	query_id = []
	foundTaxa = []
	search_resp = False
	out_name = None

	if rank == 'sp' or rank == u'sp':
		rank = u'sp.'
	if rank == 'gen' or rank == u'gen':
		rank = u'gen.'

	query = u"{0}name/search?apikey={1}&name={2}&format=json".format(service, api_key, url_name)
	#print query
	req = urllib2.Request(query)
	resp = None
	result = None
	try:
		resp = urllib2.urlopen(req)
	except urllib2.HTTPError:
		pass
	except:
		raise

	if resp:
		result = json.loads(resp.read())
	else:
		return (in_name, None)

	#print result
	if not u"Error" in result[0]:
		#print "got something"
		for item in result:
			#print item
			if item[u'ScientificName'] == name and item[u'RankAbbreviation'] == rank:
				if item[u'NomenclatureStatusName'] in [u'Invalid', u'Illegitimate', u'nom. rej.']:
					# Name is rubbish
					out_name = None

				elif item[u'NomenclatureStatusName'] in [u'No opinion', u'nom. cons.', u'Legitimate']:
					query_id.append(item[u'NameId'])
					tname = otu()
					tname.year = extract_year(item[u'DisplayDate'])
					tname.from_string(item[u'ScientificName'])
					tname.author = item[u'ScientificNameWithAuthors'].lstrip(item[u'ScientificName'])
					tname.family = item[u'Family']
					foundTaxa.append(tname)
					search_resp = True

				else:
					print "Nomenclatural status:",item[u'NomenclatureStatusName']
			else:
				out_name = None

		#print search_name, search_year

		if len(query_id) > 1:
			#print "Multiple matches for",name,":",query_id
			foundTaxa = filter(lambda x: isinstance(x.year, int), foundTaxa)
			#print foundTaxa
			if len(foundTaxa) > 1:
				foundTaxa = [sorted(foundTaxa, key=lambda x: x.year)[0]]
			#print foundTaxa
			#print "Selected year:", foundTaxa[0].year

		if len(foundTaxa) == 1 and search_resp:
			search_name = foundTaxa[0]
			accepted_name = otu()
			accepted_name.year = 0
			accepted_resp = False
			synonym_name = otu()
			synonym_name.year = 0
			synonym_resp = False

			# get accepted names
			query = "{0}name/{1}/acceptednames?apikey={2}&format=json".format(service, query_id[0], api_key)

			req = urllib2.Request(query)
			resp = urllib2.urlopen(req)
			result = json.loads(resp.read())
			#print result

			if not u"Error" in result[0]:
				accepted_resp = True
				for item in result:
					tyear = extract_year(item[u'Reference'][u'TitlePageYear'])
					if tyear > accepted_name.year:
						accepted_name.year = tyear
						accepted_name.from_string(item[u'AcceptedName'][u'ScientificName'])
						accepted_author = item[u'AcceptedName'][u'ScientificNameWithAuthors'].lstrip(item[u'AcceptedName'][u'ScientificName'])
						accepted_name.family = item[u'AcceptedName'][u'Family']

			# get synonyms
			query = "{0}name/{1}/synonyms?apikey={2}&format=json".format(service, query_id[0], api_key)

			req = urllib2.Request(query)
			resp = urllib2.urlopen(req)
			result = json.loads(resp.read())
			#print result

			if not u"Error" in result[0]:
				synonym_resp = True
				for item in result:
					if u'TitlePageYear' in item[u'Reference']:
						tyear = extract_year(item[u'Reference'][u'TitlePageYear'])
						if tyear > synonym_name.year:
							synonym_name.year = tyear
							synonym_name.from_string(item[u'SynonymName'][u'ScientificName'])
							synonym_name.author = item[u'SynonymName'][u'ScientificNameWithAuthors'].lstrip(item[u'SynonymName'][u'ScientificName'])
							synonym_name.family = item[u'SynonymName'][u'Family']

			#print search_name.year, search_resp
			#print accepted_name.year, accepted_resp
			#print synonym_name.year, synonym_resp

			if accepted_name.year > 0 and synonym_name.year > 0 and accepted_resp and synonym_resp:
				if accepted_name.year > synonym_name.year:
					out_name = accepted_name

				elif accepted_name.year <= synonym_name.year:
					out_name = search_name

			elif accepted_name.year > 0 and accepted_resp:
				if search_name.year < accepted_name.year:
					out_name = accepted_name

				else:
					out_name = search_name

			elif (synonym_name.year > 0 and synonym_resp) or search_resp:
				out_name = search_name

			else:
				out_name = None


		out = (in_name, out_name)
	else:
		out = (in_name, None)

	return out


def ipni(name):
	service = u" http://www.ipni.org/ipni/advPlantNameSearch.do?"

	if isinstance(name, str):
		name = name.decode('utf8')
	if not isinstance(name, unicode):
		raise TypeError("Query should be a string or unicode.")

	in_name = otu()
	out_name = None
	in_name.from_string(name)

	if in_name.genus and in_name.epithet:
		query = u"{0}find_genus={1}&find_species={2}&find_rankToReturn=spec&output_format=delimited-extended".format(service, in_name.genus, in_name.epithet)
	elif in_name.genus:
		query = u"{0}find_genus={1}&find_rankToReturn=gen&output_format=delimited-extended".format(service, in_name.genus)
	else:
		raise ValueError

	#print query

	req = urllib2.Request(query)
	resp = urllib2.urlopen(req)
	#result = json.loads(resp.read())
	result = resp.read()
	#print result

	if result:
		out_name = out()
		out_name.year = 0
		lines = result.split('\n')
		cols = []
		cols_size = 0
		genus_i = None
		species_i = None
		year_i = None
		family_i = None
		for il,line in enumerate(lines):
			line = line.rstrip()
			if line:
				tname = otu()
				bits = line.split('%')
				if bits and len(bits) > 4:
				#print "bits length:",len(bits)

					if il == 0:
						cols = bits
						cols_size = len(cols)
						for ind, co in enumerate(cols):
							if co == 'Genus':
								genus_i = ind
							elif co == 'Species':
								species_i = ind
							elif co == 'Publication year':
								year_i = ind
							elif co == 'Family':
								family_i = ind
					elif len(bits) == cols_size and year_int:
						#print bits[year_i], bits[genus_i], bits[species_i] , bits[family_i]
						if len(bits[year_i]) == 4:
							tname.year = int(bits[year_i])
						else:
							tname.year = 1
						tname.genus = bits[genus_i]
						tname.epithet = bits[species_i]
						tname.family = bits[family_i]

						if tname.year < out_name.year:
							out_name = tname
			if out_name.family is None and out_name.genus is None:
				out_name = None

	return (in_name, out_name)
