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

def get_density(genus, epitet, wd_data, family = None):
	"""
	Retrieves wood density of a taxon.
	"""
	pass

def interpolate(wd_data, genus, family):
	"""
	Interpolate wood density value from available data. Requires at least genus
	info.
	"""
	pass
