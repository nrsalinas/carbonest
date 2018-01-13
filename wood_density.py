"""
Wood density functions.
"""
from math import log, exp
from pandas import isna, notna


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
					family = bits[1].title()
					if len(tidbits) == 2:
						genus = tidbits[0].title()
						epitet = tidbits[1].lower()
					elif len(tidbits) == 1:
						genus = tidbits[0].title()
						epitet = None
					elif len(tidbits) == 3 and tidbits[1].upper() == "X":
						genus = tidbits[0].title()
						epitet = tidbits[2].lower()
					if family not in out:
						out[family] = {genus: { epitet: [float(bits[3])]}}
					elif genus not in out[family]:
						out[family][genus] = {epitet: [float(bits[3])]}
					elif epitet not in out[family][genus]:
						out[family][genus][epitet] = [float(bits[3])]
					else:
						out[family][genus][epitet].append(float(bits[3]))
	return out


def get_density(family, genus, epithet, wd_data):
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
	out = None
	if notna(family):
		family = family.title()
	if notna(genus):
		genus = genus.title()
	if notna(epithet):
		epithet = epithet.lower()

	if notna(family) and family in wd_data:
		out = 0.0
		if notna(genus) and genus in wd_data[family]:
			if notna(epithet) and epithet in wd_data[family][genus]:
				if len(wd_data[family][genus][epithet]) >= 1:
					out = sum(wd_data[family][genus][epithet])
					out /= len(wd_data[family][genus][epithet])
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



def pnt(depth, iters = 20):
	"""
	Estimates wood density from penetrometer data.

	Arguments:

	- depth (float): Maximum distance reached into the wood sample (cm) after 20
	hit iterations. Should be less or equal to 20 cm.

	- iters (int): Number of 1 Kgr hits. Should be less than 20.

	"""
	out = 0.0
	I = 0
	P = 0
	if 0 < depth <= 20 and 1 < iters <= 20 and \
		((iters < 20 and depth == 20) or (iters == 20 and depth <= 20)):

		if depth > 1:
			I = 1

		if iters == 20:
			P = depth / 20.0

	 	elif iters < 20:
			P = 20.0 / (iters - 0.5)

		out = 0.6451 - 0.388 * log(depth, 10) - 0.377 * I + 0.3 * log(depth, 10)

	else:
		raise ValueError("Non valid values of penetrometer depth ({0}) and drop iterations ({1}).".format(depth, iters))

	return out
