"""
Wood density functions.
"""

def load_data(csv_file):
	"""
	Loads wood density values from a csv table. Columns in the file should follow
	the order presented by Chave et al. in the Global Wood Density Database
	(http://datadryad.org/handle/10255/dryad.235): index, family, species name,
	wood density, region, and reference number. Returns a 2-dimensional
	dictionary (dict[Family][Species] = list of wood density values).

	Arguments:

	- csv_file (str): Path to the woo density data file.

	"""
	out = {}
	with open(csv_file,"r") as fh:
		for ir, row in enumerate(fh):
			if ir > 0:
				bits = row.split(",")
				if bits[1] and bits[2] and bits[3]:
					tidbits = bits[2].split(" ")
					genus = tidbits[0]
					epitet = tidbits[1]
					if bits[1] not in out:
						out[bits[1]] = {genus: { epitet: [float(bits[3])]}}
					elif genus not in out[bits[1]]:
						out[bits[1]][genus] = {epitet: [float(bits[3])]}
					elif epitet not in out[bits[1]][genus]:
						out[bits[1]][genus][epitet] = [float(bits[3])]
					else:
						out[bits[1]][genus][epitet].append(float(bits[3]))
	return out


def get_density(family, genus, epitet, wd_data):
	"""
	Retrieves wood density of a taxon from a wood density database object. If
	the species or genus is not included in the DB, an average of the associated
	genus or family is retrieved, respectively. Returns a float.

	Arguments:

	- family (str): Botanical family. Should follow APGIV classification system.

	- genus (str): Botanical genus.

	- epitet (str): Species epitet.

	- wd_data (dict): Data base with wood density values as loaded by function
	wood_density.load_data.

	"""
	out = 0.0
	if family is not None and family in wd_data:
		if genus is not None and genus in wd_data[family]:
			if epitet is not None and epitet in wd_data[family][genus]:
				if len(wd_data[family][genus][epitet]) >= 1:
					out = sum(wd_data[family][genus][epitet])
					out /= len(wd_data[family][genus][epitet])
				else:
					print "{0} {1} included in the wood density DB but no values associated.".format(genus, epitet)
			else:
				spp_count = 0
				for other_sp in wd_data[family][genus]:
					out += sum(wd_data[family][genus][other_sp])
					spp_count += len(wd_data[family][genus][other_sp])
				out /= spp_count
		else:
			spp_count = 0
			for other_gen in wd_data[family]:
				for other_sp in wd_data[family][other_gen]:
					out += sum(wd_data[family][other_gen][other_sp])
					spp_count += len(wd_data[family][other_gen][other_sp])
			out /= spp_count
	return out
