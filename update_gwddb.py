import pandas as pd
import numpy as np
import taxon


gw = pd.read_csv('/home/nelson/Documents/IDEAM/GlobalWoodDensityDB/gwddb_original.csv')
gw.Binomial = gw.Binomial.str.replace(r' indet$', '')

gw[u'newFamily'] = np.nan
gw[u'newTaxon'] = np.nan

spp = {x:(None,None) gw.Binomial.unique().tolist()

for s in xrange(0, len(spp), 200):
	e = s + 200
	if e > len(spp):
		e = len(spp)

	tnrs = taxon.check_names(spp.keys()[s:e], accepted=True)

	for tns in tnrs:

		if tns[u'resp'][u'genus'] is None or tns[u'resp'][u'family'] is None \
			or (tns[u'query'][u'epithet'] is not None and tns[u'resp'][u'epithet'] is None):

			#print "Checking Tropicos..."

			if tns[u'resp'][u'epithet']:
				rank = 'sp'
			else:
				rank = 'gen'

			name = ' '.join([tns[u'query'][u'genus'],tns[u'query'][u'epithet']])
			#print name, rank
			trop = taxon.tropicos(name, rank)
			if trop[u'resp'] is None:
				qname = ' '.join([tns[u'query'][u'genus'], tns[u'query'][u'epithet']])
				rname = ' '.join([tns[u'resp'][u'genus'], tns[u'resp'][u'epithet']])
				rfamily = tns[u'resp'][u'family']

			else:
				#print trop[u'resp'][u'genus'], trop[u'resp'][u'epithet']
				qname = ' '.join([trop[u'query'][u'genus'], trop[u'query'][u'epithet']])
				rname = ' '.join([trop[u'resp'][u'genus'], trop[u'resp'][u'epithet']])
				rfamily = trop[u'resp'][u'family']

		elif tns[u'resp'][u'epithet']:
			newspp.append(' '.join([tns[u'resp'][u'genus'], tns[u'resp'][u'epithet']]))
			family.append(tns[u'resp'][u'family'])

		else:
			newspp.append(tns[u'resp'][u'genus'])
			family.append(tns[u'resp'][u'family'])


		spp[qname][(rname, rfamily)]
