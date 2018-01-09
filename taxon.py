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

	def unicode(self, author = False):
		out = ""
		if self.genus:
			if self.epithet:
				if self.infraRank and self.infraEpithet:
					out = self.genus + u" " + self.epithet + u" " + self.infraRank + u" " + self.infraEpithet
				else:
					out = self.genus + u" " + self.epithet
			else:
				out = self.genus
		elif self.family:
			out = self.family
		if author:
			out += u" " + self.author
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


def check_names(names, minimum_score = 0.95 ,
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

	- minimum_score (float):

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
			pass
	elif isinstance(names, str):
		names = url_space(names).decode('utf-8')
	elif isinstance(names, unicode):
		pass
	else:
		checked = None ### Throw TypeError

	query = u"{0}?retrieve={1}&names={2}".format(tnrs_url, resLevel, names)

	req = urllib2.Request(query)
	resp = urllib2.urlopen(req)
	result = json.loads(resp.read())

	#print result

	for nami in result[u'items']:

		out = {
			u"resp": {
				u"family" : None,
				u"genus" : None,
				u"epithet" : None,
				u"infraRank" : None,
				u"infraEpithet" : None,
				u"author" : None,
				u"score" : None
				},

			u"query": None
			}

		# get a dict similar to out[u"resp"] for the queried name
		out[u"query"] = split_name(nami[u'nameSubmitted'])

		if nami[u'scientificScore']:
			nami[u'scientificScore'] = float(nami[u'scientificScore'])
			out[u"resp"][u"score"] = nami[u'scientificScore']
			if nami[u'genusScore']:
				nami[u'genusScore'] = float(nami[u'genusScore'])
			if nami[u'scientificScore'] >= minimum_score or nami[u'genusScore'] == 1: # Correct name in nami[nameScientific]

				if nami[u'family']:
					out[u"resp"][u"family"] = nami[u'family']

				if accepted and nami[u'acceptedName']:
					bits = nami[u'acceptedName'].split(u' ')
					out[u"resp"][u"genus"] = bits[0]
					out[u"resp"][u"author"] = nami[u'acceptedAuthor']

					if len(bits) == 2:
						out[u"resp"][u"epithet"] = bits[1]

					if len(bits) == 4:
						out[u"resp"][u"epithet"] = bits[1]
						out[u"resp"][u"infraRank"] = bits[2]
						out[u"resp"][u"infraEpithet"] = bits[3]

				else:
					if nami[u'genusScore']:
						nami[u'genusScore'] = float(nami[u'genusScore'])
						out[u"resp"][u"genus"] = nami[u'genus']
						out[u"resp"][u"family"] = nami[u'family']

						if nami[u'epithetScore']:
							nami[u'epithetScore'] = float(nami[u'epithetScore'])
							out[u"resp"][u"epithet"] = nami[u'epithet']

							if nami[u'infraspecific1EpithetScore']:
								nami[u'infraspecific1EpithetScore'] = float(nami[u'infraspecific1EpithetScore'])
								out[u"resp"][u"infraEpithet"] = nami[u'infraspecific1Epithet']

								if nami[u'nameScientific'].find(u' var. ') >= 0:
									out[u"resp"][u"infraRank"] =  u"var."
								elif nami[u'nameScientific'].find(u' subsp. ') >= 0:
									out[u"resp"][u"infraRank"] =  u"subsp."

							# authorAttributed always retrieved
							if nami[u'authorAttributed']:
								out[u"resp"][u"author"] = nami[u'authorAttributed']

					# authorScore only retrieved if queried author starts with upper case
					#if nami[u'authorScore']:
					#	nami[u'authorScore'] = float(nami[u'authorScore'])
					#	myAuthor = nami[u'author']

		checked.append(out)

	return checked

def extract_year(tropicos_string):
	out = None
	bits = re.split(r'\s+', tropicos_string)
	bits = map(lambda x: re.sub(r'\D','',x), bits)
	bits = filter(lambda x: len(x) >= 4, bits)

	if len(bits):
		bits = map(int, bits)
		bits = sorted(bits, reverse = True)
		out = bits[0]
		if bits[0] > 2017:
			print "This was printed in the future:", bits[0]

	return out


def tropicos(name, rank, file_api_key = "tropicos_api_key"):
	"""
	rank : `sp` or `gen`
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

	in_name = split_name(name)
	url_name = url_space(name)
	query_id = []
	search_year = 0
	search_name = u''
	search_author = u''
	search_family = u''
	search_resp = False

	out_name = {}

	if rank == 'sp' or rank == u'sp':
		rank = u'sp.'
	if rank == 'gen' or rank == u'gen':
		rank = u'gen.'

	query = u"{0}name/search?apikey={1}&name={2}&format=json".format(service, api_key, url_name)

	req = urllib2.Request(query)
	resp = urllib2.urlopen(req)
	result = json.loads(resp.read())

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
					search_year = extract_year(item[u'DisplayDate'])
					search_name = item[u'ScientificName']
					search_author = item[u'ScientificNameWithAuthors'].lstrip(search_name)
					search_family = item[u'Family']
					search_resp = True

				else:
					print "Nomenclatural status:",item[u'NomenclatureStatusName']
			else:
				out_name = None

		#print search_name, search_year

		if len(query_id) > 1:
			print "Multiple matches for",name,":",query_id


		elif len(query_id) == 1 and search_resp:
			accepted_year = 0
			accepted_name = u""
			accepted_author = u""
			accepted_family = u""
			accepted_resp = False
			synonym_year = 0
			synonym_name = u""
			synonym_author = u""
			synonym_family = u""
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
					if tyear > accepted_year:
						accepted_year = tyear
						accepted_name = item[u'AcceptedName'][u'ScientificName']
						accepted_author = item[u'AcceptedName'][u'ScientificNameWithAuthors'].lstrip(accepted_name)
						accepted_family = item[u'AcceptedName'][u'Family']

			# get synonyms
			query = "{0}name/{1}/synonyms?apikey={2}&format=json".format(service, query_id[0], api_key)

			req = urllib2.Request(query)
			resp = urllib2.urlopen(req)
			result = json.loads(resp.read())
			#print result

			if not u"Error" in result[0]:
				synonym_resp = True
				for item in result:
					tyear = extract_year(item[u'Reference'][u'TitlePageYear'])
					if tyear > synonym_year:
						synonym_year = tyear
						synonym_name = item[u'SynonymName'][u'ScientificName']
						synonym_author = item[u'SynonymName'][u'ScientificNameWithAuthors'].lstrip(synonym_name)
						synonym_family = item[u'SynonymName'][u'Family']

			if accepted_year > 0 and synonym_year > 0 and accepted_resp and synonym_resp:
				if accepted_year > synonym_year:
					out_name = split_name(accepted_name)
					out_name[u'family'] = accepted_family
					out_name[u'author'] = accepted_author
				elif accepted_year < synonym_year:
					out_name = split_name(synonym_name)
					out_name[u'family'] = synonym_family
					out_name[u'author'] = synonym_author

			elif accepted_year > 0 and accepted_resp:
				if search_year < accepted_year:
					out_name = split_name(accepted_name)
					out_name[u'family'] = accepted_family
					out_name[u'author'] = accepted_author
				else:
					out_name = split_name(search_name)
					out_name[u'family'] = search_family
					out_name[u'author'] = search_author

			elif synonym_year > 0 and synonym_resp:
				if search_year < synonym_year:
					out_name = split_name(synonym_name)
					out_name[u'family'] = synonym_family
					out_name[u'author'] = synonym_author
				else:
					out_name = split_name(search_name)
					out_name[u'family'] = search_family
					out_name[u'author'] = search_author

			elif search_year > 0 and search_resp:
				out_name = split_name(search_name)
				out_name[u'family'] = search_family
				out_name[u'author'] = search_author

			else:
				out_name = None

			#print "accepted_resp", accepted_resp, "query_resp", query_resp

		out = {u'query': in_name, u'resp':out_name}
	else:
		out = {u'query': in_name, u'resp': None}
	#print "search_resp", search_resp

	return out
