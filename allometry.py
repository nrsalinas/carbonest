#import gdal
import numpy as np

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
	Retrieves E value for a given location, as proposed by Chave et al. 2014
	(Global Change Biology 20: 3177-3190, eq 6A & 6B). Requires the raster file
	provided by Chave and available at
	http://chave.ups-tlse.fr/pantropical_allometry/E.bil.zip. Returns a float.
	"""
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

	return intval[0][0]


def chave_height(diameter, longitude, latitude, raster_file):
	"""
	Estimates tree height accordingly to allometric relation proposed by Chave
	et al. 2014 (Global Change Biology 20: 3177-3190, eq 6A).
	"""
	E = getE(longitude, latitude, raster_file)
	logH = 0.893 - E + 0.760 * np.log(diameter) - 0.0340 * np.log(diameter)**2
	height = np.exp(logH + 0.5 * 0.243**2)
	return height

###################################
# Volume estimation functions
###################################

def chaveI(diameter, density, forest_type):
	"""
	Estimates tree biomass (gr) through the allometric equation proposed by
	Chave et al. Oecologia 145: 87-99 (Chave I). Returns a float.

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
