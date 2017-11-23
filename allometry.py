import gdal
import numpy as np

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
	(Global Change Biology 20: 3177–3190, eq 6A & 6B). Requires the raster file 
	provided by Chave and available at 
	http://chave.ups-tlse.fr/pantropical_allometry/E.bil.zip 
	Returns a float.

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


def chave(diameter, longitude, latitude, raster_file):
	"""
	Estimates tree height accordingly to allometric relation proposed by Chave et 
	al. 2014	(Global Change Biology 20: 3177–3190, eq 6A). 
	"""
	E = getE(longitude, latitude, raster_file)
	logH = 0.893 - E + 0.760 * np.log(diameter) - 0.0340 * np.log(diameter)**2
	height = np.exp(logH + 0.5 * 0.243**2)
	return height

