import numpy as np

GDAL = 0
try:
	import gdal
	GDAL = 1
except ImportError as e:
	if e.message == "No module named gdal":
		print "Warning: functions based on data from raster files will not be available. "
	else:
		raise
except:
	raise

###################################
# Height estimation functions
###################################

def weibull(diameter, a = 42.574, b = 0.0482, c = 0.8307):
	"""
	Weibull function to estimate tree height (Feldpausch et al. 2012,
	Biogeosciences 9:3381-3403, eq 5). Requires know values of coefficients
	a, b, and c.

	"""
	height = a * (1.0-np.exp(-b * diameter ** c))
	return height


def getE(longitude, latitude, raster_file):
	"""
	Retrieves E value for a given location, as proposed by Chave et al. 2014,
	Global Change Biology 20: 3177-3190, eq 6A & 6B). Requires the raster file
	provided by Chave and available at
	http://chave.ups-tlse.fr/pantropical_allometry/E.bil.zip. Returns a float.
	"""
	out = None

	if GDAL:
		E_raster = gdal.Open(raster_file)
		transform = E_raster.GetGeoTransform()
		xOrigin = transform[0]
		yOrigin = transform[3]
		pixelWidth = transform[1]
		pixelHeight = transform[5]
		E_band = E_raster.GetRasterBand(1)
		px = int((longitude - xOrigin) / pixelWidth) #x pixel
		py = int((latitude - yOrigin) / pixelHeight) #y pixel
		intval = E_band.ReadAsArray(px,py,1,1)
		out = intval[0][0]

	else:
		print "Function getE is not available: requires package gdal."

	return out


def chave_height(diameter, longitude, latitude, raster_file):
	"""
	Estimates tree height accordingly to allometric relation proposed by Chave
	et al. 2014 (Global Change Biology 20: 3177-3190, eq 6A).
	"""
	height = None

	if GDAL:
		E = getE(longitude, latitude, raster_file)
		logH = 0.893 - E + 0.760 * np.log(diameter) - 0.0340 * np.log(diameter)**2
		height = np.exp(logH + 0.5 * 0.243**2)

	else:
		print "Function chave_height is not available: requires package gdal."

	return height

###################################
# Biomass estimation functions
# requiring only diameter 
###################################

def chaveI(diameter, density, forest_type):
	"""
	Estimates tree biomass (gr) through the allometric equation proposed by
	Chave et al. 2005, Oecologia 145: 87-99 (Chave I). Returns a float.

	Arguments:

	- diameter (float): Diameter (cm) at breast height of the tree.

	- density (float); Wood density (gr/cm^3).

	- forest_type (str): Climatic clasification of the sampling site. Valid
	values are `dry`, `moist`, and `wet`.

	"""

	AGB = 0
	c = 0.207 * np.log(diameter)**2
	d = -0.028 * np.log(diameter)**3

	if forest_type == 'dry':

		a = -0.667
		b = 1.784 * np.log(diameter)
		AGB = density * np.exp(a + b + c + d)

	elif forest_type == 'moist':

		a = -1.499
		b = 2.148 * np.log(diameter)
		AGB = density * np.exp(a + b + c + d)

	elif forest_type == 'wet':

		a = -1.239
		b = 1.980 * np.log(diameter)
		AGB = density * np.exp(a + b + c + d)

	else:
		raise ValueError

	return AGB


def alvarez(diameter, density, forest_type):
	"""
	Estimates tree biomass (gr) through the allometric equations type II.1
	proposed by Alvarez et al. 2013, Forest Ecology and Managament 267: 297-308. Returns a float.

	Arguments:

	- diameter (float): Diameter (cm) at breast height of the tree.

	- density (float); Wood density (gr/cm^3).

	- forest_type (str): Climatic clasification of the sampling site. Valid
	values are `tropical_dry`, `tropical_moist`, `tropical_wet`,
	`premontane_moist`, `lower_montane_wet`, `montane_wet`.

	"""

	AGB = 0
	c = 1.169 * np.log(diameter)**2
	d = -0.122 * np.log(diameter)**3

	if forest_type == 'tropical_dry':

		a = 3.652
		b = -1.697 * np.log(diameter)
		e = 1.285 * np.log(density)
		AGB = np.exp(a + b + c + d + e)

	elif forest_type == 'tropical_moist':

		a = 2.406
		b = -1.289 * np.log(diameter)
		e = 0.445 * np.log(density)
		AGB = np.exp(a + b + c + d + e)

	elif forest_type == 'tropical_wet':

		a = 1.662
		b = -1.114 * np.log(diameter)
		e = 0.331 * np.log(density)
		AGB = np.exp(a + b + c + d + e)

	elif forest_type == 'premontane_moist':

		a = 1.960
		b = -1.098 * np.log(diameter)
		e = 1.061 * np.log(density)
		AGB = np.exp(a + b + c + d + e)

	elif forest_type == 'lower_montane_wet':

		a = 1.836
		b = -1.255 * np.log(diameter)
		e = -0.222 * np.log(density)
		AGB = np.exp(a + b + c + d + e)

	elif forest_type == 'montane_wet':

		a = 3.130
		b = -1.536 * np.log(diameter)
		e = 1.767 * np.log(density)
		AGB = np.exp(a + b + c + d + e)

	else:
		raise ValueError

	return AGB


def chaveII(diameter, density, longitud, latitude, raster_file):
	"""
	Estimates tree biomass (gr) through the allometric equation proposed by
	Chave et al. 2014, Global Change Biology 20: 3177-3190 (Chave II). Returns a
	float.

	Arguments:

	- diameter (float): Diameter (cm) at breast height of the tree.

	- density (float); Wood density (gr/cm^3).

	- longitud, latitude (float): Geographic coordinates of the sampling site.

	-raster_file (str): Path to the raster file of E as distributed by Chave.

	"""
	AGB = None
	if GDAL:
		E = getE(longitude, latitude, raster_file)

		AGB = np.exp(-1.802 - 0.976 * E + 0.976 * np.log(density) +
				2.673 * np.log(diameter) - 0.029 * np.log(diameter)**2)

	else:
		print "Function chave_height is not available: requires package gdal."

	return AGB
