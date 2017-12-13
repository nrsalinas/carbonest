import urllib2
import json

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
	elif isinstance(names, str):
		names = url_space(names).decode('utf-8')
	else:
		checked = None ### Throw TypeError

	query = u"{0}?retrieve={1}&names={2}".format(tnrs_url, resLevel, names)

	req = urllib2.Request(query)
	resp = urllib2.urlopen(req)
	result = json.loads(resp.read())

	for nami in result[u'items']:

		myGenus = None
		myEpithet = None
		myInfraRank = None
		myInfraEpithet = None
		myAuthor = None

		if nami[u'scientificScore']:
			nami[u'scientificScore'] = float(nami[u'scientificScore'])
			if nami[u'scientificScore'] >= minimum_score: # Correct name in nami[nameScientific]

				if accepted and nami[u'acceptedName']:
					bits = nami[u'acceptedName'].split(u' ')
					myGenus = bits[0]
					myAuthor = nami[u'acceptedAuthor']

					if len(bits) == 2:
						myEpithet = bits[1]

					if len(bits) == 4:
						myEpithet = bits[1]
						myInfraRank = bits[2]
						myInfraEpithet = bits[3]

				else:
					if nami[u'genusScore']:
						nami[u'genusScore'] = float(nami[u'genusScore'])
						myGenus = nami[u'genus']

						if nami[u'epithetScore']:
							nami[u'epithetScore'] = float(nami[u'epithetScore'])
							myEpithet = nami[u'epithet']

							if nami[u'infraspecific1EpithetScore']:
								nami[u'infraspecific1EpithetScore'] = float(nami[u'infraspecific1EpithetScore'])
								myInfraEpithet = nami[u'infraspecific1Epithet']

								if nami[u'nameScientific'].find(u' var. ') >= 0:
									myInfraRank = u"var."
								elif nami[u'nameScientific'].find(u' subsp. ') >= 0:
									myInfraRank = u"subsp."

							# authorAttributed always retrieved
							if nami[u'authorAttributed']:
								myAuthor = nami[u'authorAttributed']

					# authorScore only retrieved if queried author starts with upper case
					#if nami[u'authorScore']:
					#	nami[u'authorScore'] = float(nami[u'authorScore'])
					#	myAuthor = nami[u'author']


		checked.append((myGenus, myEpithet, myInfraRank, myInfraEpithet, myAuthor))

	return checked
