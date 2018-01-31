import numpy as np
import os

np.seterr(over='raise')

GDAL = 0
try:
	import gdal
	GDAL = 1
except ImportError as e:
	if e.message == "No module named gdal":
		print "Warning: functions based on data from raster files will not be available. "
	else:
		#raise
		pass
except:
	raise


def altitude(longitude, latitude, raster):
	"""
	rasters = Iterable of raster file paths where the location maybe be found.
	"""
	out = None
	radius = 0
	if GDAL:
		while out is None:
			alt = []
			myras = gdal.Open(raster)
			transform = myras.GetGeoTransform()
			xOrigin = transform[0]
			yOrigin = transform[3]
			pixelWidth = transform[1]
			pixelHeight = transform[5]
			px = int((longitude - xOrigin) / pixelWidth) #x pixel
			py = int((latitude - yOrigin) / pixelHeight) #y pixel
			pxs = [px-radius, px+radius]
			pys = [py-radius, py+radius]
			for npx in pxs:
				for npy in pys:
					if npx > 0 and npy > 0 and npx <= myras.RasterXSize and npy <= myras.RasterYSize:
						intval = myras.ReadAsArray(npx,npy,1,1)
						if intval[0][0] > -100:
							alt.append(intval[0][0])
			alt = filter(lambda w: abs(w) != np.inf, alt)
			if len(alt):
				out = sum(alt) / float(len(alt))
			radius += 1

	return out


def precipitation_old(longitude, latitude, raster_files):
	"""
	Estimates yearly aggregated precipitation from monthly data.

	- raster_files (str): Path to raster files of monthly precipitation. Should
	follow WorldClim v2 filename standard (*.tif).
	"""
	out = None
	radius = 0
	if GDAL:
		out = -1
		while out < 0:
			month_prec = []
			for myfile in os.listdir(raster_files):
				if myfile.endswith('.tif') or myfile.endswith('.bil'):
					prec_raster = gdal.Open(raster_files + '/' + myfile)
					transform = prec_raster.GetGeoTransform()
					xOrigin = transform[0]
					yOrigin = transform[3]
					pixelWidth = transform[1]
					pixelHeight = transform[5]
					prec_band = prec_raster.GetRasterBand(1)
					px = int((longitude - xOrigin) / pixelWidth) #x pixel
					py = int((latitude - yOrigin) / pixelHeight) #y pixel
					pxs = [px-radius, px+radius]
					pys = [py-radius, py+radius]
					for npx in pxs:
						for npy in pys:
							intval = prec_band.ReadAsArray(npx,npy,1,1)
							if intval[0][0] > 0:
								month_prec.append(intval[0][0])

			if len(month_prec):
				out = (sum(month_prec) / float(len(month_prec))) * 12

			radius += 1

	return out

def precipitation(longitude, latitude, raster_file):
	"""
	Estimates yearly aggregated precipitation from monthly data.

	- raster_files (str): Raster files of annual precipitation. Should
	follow WorldClim v2 filename standard (*.tif).
	"""
	out = None
	radius = 0
	if GDAL:
		out = -1
		while out < 0:
			prec = []
			if raster_file.endswith('.tif') or raster_file.endswith('.bil'):
				prec_raster = gdal.Open(raster_file)
				transform = prec_raster.GetGeoTransform()
				xOrigin = transform[0]
				yOrigin = transform[3]
				pixelWidth = transform[1]
				pixelHeight = transform[5]
				prec_band = prec_raster.GetRasterBand(1)
				px = int((longitude - xOrigin) / pixelWidth) #x pixel
				py = int((latitude - yOrigin) / pixelHeight) #y pixel
				pxs = [px-radius, px+radius]
				pys = [py-radius, py+radius]
				for npx in pxs:
					for npy in pys:
						if npx > 0 and npy > 0 and npx <= prec_raster.RasterXSize and npy <= prec_raster.RasterYSize:
							intval = prec_band.ReadAsArray(npx,npy,1,1)
							if intval[0][0] > 0:
								prec.append(intval[0][0])
				prec = filter(lambda w: abs(w) != np.inf, prec)
			if len(prec):
				out = sum(prec) / float(len(prec))

			radius += 1

	return out

def holdridge_col(altitude, precipitation):
	"""
	Estimates the life zone according to Holdridge (1971, `Forest Environments in
	Tropical Life Zones: A Pilot Study`). Only estimates forest life zones.
	Arguments are altitude (m) and precipitation (mm / year).
	"""
	out = None
	if altitude < 1000:
		if 500 <= precipitation < 1000:
			out = 'tropical_very_dry'
		elif 1000 <= precipitation < 2000:
			out = 'tropical_dry'
		elif 2000 <= precipitation < 4000:
			out = 'tropical_moist'
		elif 4000 <= precipitation < 8000:
			out = 'tropical_wet'
		elif 8000 <= precipitation:
			out = 'tropical_rain'
		else:
			pass
	elif 1000 <= altitude < 2000:
		if 500 <= precipitation < 1000:
			out = 'premontane_dry'
		elif 1000 <= precipitation < 2000:
			out = 'premontane_moist'
		elif 2000 <= precipitation < 4000:
			out = 'premontane_wet'
		elif 4000 <= precipitation < 8000:
			out = 'premontane_rain'
		else:
			pass
	elif 2000 <= altitude < 3000:
		if 500 <= precipitation < 1000:
			out = 'lower_montane_dry'
		elif 1000 <= precipitation < 2000:
			out = 'lower_montane_moist'
		elif 2000 <= precipitation < 4000:
			out = 'lower_montane_wet'
		elif 4000 <= precipitation < 8000:
			out = 'lower_montane_rain'
		else:
			pass
	elif 3000 <= altitude < 4000:
		if 500 <= precipitation < 1000:
			out = 'montane_moist'
		elif 1000 <= precipitation < 2000:
			out = 'montane_wet'
		elif 2000 <= precipitation < 4000:
			out = 'montane_wet'
		else:
			pass
	else:
		pass

	return out




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
	min_value = -10.0

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
		out = float(intval[0][0])

		# Sampling neighbors if E in px,py is -inf
		rad = 1
		while abs(out) == np.inf or out < min_value:
			newee = []
			for pxi in [(px-rad), (px+rad)]:
				for pyi in [(py-rad),(py+rad)]:
					if pxi > 0 and pyi > 0 and pxi <= E_raster.RasterXSize and pyi <= E_raster.RasterYSize:
						intval = E_band.ReadAsArray(pxi,pyi,1,1)
						newee.append(float(intval[0][0]))
			newee = filter(lambda w: abs(w) != np.inf, newee)
			newee = filter(lambda w: w > min_value, newee)
			if len(newee):
				out = sum(newee) / len(newee)
			rad += 1

	else:
		print "Function getE is not available: requires package gdal."

	return out


def chaveI_forest(precipitation):
	"""
	Estimate the forest type according to Chave et al. 2005, Oecologia 145: 87-99.
	Returns a str. Precipitation should be a numerical value in the form mm / year.

	Possible output categories:

	- 'wet': Evapotranspiration exceeds rainfall during a month or less (rainfall
	> 3500 mm / year).

	- 'moist': Evapotranspiration exceeds rainfall for 1-5 months a year (rainfall
	in the range 1500-3500 mm / year).

	- 'dry': Evapotranspiration exceeds rainfall more than 5 months a year (rainfall
	 < 1500 mm / year).
	"""

	out = None

	if precipitation <= 1500:
		out = 'dry'
	elif precipitation <= 3500:
		out = 'moist'
	else:
		out = 'wet'

	return out


def chave_height(diameter, longitude=None, latitude=None, raster_file = None, e_value = None):
	"""
	Estimates tree height accordingly to allometric relation proposed by Chave
	et al. 2014 (Global Change Biology 20: 3177-3190, eq 6A). It is necessary to
	parse either a coefficient E value or all the info required to estimate it:
	the path to a raster file modeling E, and the geographic coordinates of the
	forest location.
	"""
	height = None

	if GDAL and longitude and latitude and raster_file and e_value is None:
		E = getE(longitude, latitude, raster_file)

	if isinstance(e_value, float):
		logH = 0.893 - E + 0.760 * np.log(diameter) - 0.0340 * np.log(diameter)**2
		height = np.exp(logH + 0.5 * 0.243**2)

	return height

###################################
# Biomass estimation functions
# requiring only diameter
###################################

def chaveI(diameter, density, forest_type):
	"""
	Estimates tree biomass (Kg) through the allometric equation proposed by
	Chave et al. 2005, Oecologia 145: 87-99 (Chave I, as published by Phillips
	et al. 2016, Forest Ecology and Management 374: 119-128). Returns a float.

	Arguments:

	- diameter (float): Diameter (cm) at breast height of the tree.

	- density (float); Wood density (gr/cm^3).

	- forest_type (str): Climatic clasification of the sampling site. Valid
	values are `dry`, `moist`, and `wet`.

	"""

	AGB = 0
	if diameter < 1e-323:
		pass
		#
		#Throw error, log will be inf
		#

	else:
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


def chaveI_original(diameter, density, forest_type):
	"""
	Estimates tree biomass (Kg) through the allometric equation proposed by
	Chave et al. 2005, Oecologia 145: 87-99 (Chave I, as published by the
	authors). Returns a float.

	Arguments:

	- diameter (float): Diameter (cm) at breast height of the tree.

	- density (float); Wood density (gr/cm^3).

	- forest_type (str): Climatic clasification of the sampling site. Valid
	values are `dry`, `moist`, and `wet`.

	"""

	AGB = 0
	if diameter < 1e-323:
		pass
		#
		#Throw error, log will be inf
		#

	else:
		c = 0.207 * np.log(diameter)**2
		d = -0.028 * np.log(diameter)**3

		if forest_type == 'dry':

			a = -0.730
			b = 1.784 * np.log(diameter)
			AGB = density * np.exp(a + b + c + d)

		elif forest_type == 'moist':

			a = -1.562
			b = 2.148 * np.log(diameter)
			AGB = density * np.exp(a + b + c + d)

		elif forest_type == 'wet':

			a = -1.302
			b = 1.980 * np.log(diameter)
			AGB = density * np.exp(a + b + c + d)

		else:
			raise ValueError

	return AGB


def alvarez(diameter, density, forest_type):
	"""
	Estimates tree biomass (Kg) through the allometric equations type II.1
	proposed by Alvarez et al. 2012, Forest Ecology and Managament 267: 297-308. Returns a float.

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


def chaveII(diameter, density, longitude = None, latitude = None, raster_file = None, e_value = None):
	"""
	Estimates tree biomass (Kg) through the allometric equation proposed by
	Chave et al. 2014, Global Change Biology 20: 3177-3190 (Chave II). It is
	necessary to parse either a coefficient E value or all the info required to
	estimate it: the path to the raster file modeling E, and the geographic
	coordinates of the forest location. Returns a float.

	Arguments:

	- diameter (float): Diameter (cm) at breast height of the tree.

	- density (float); Wood density (gr/cm^3).

	- longitud, latitude (float): Geographic coordinates of the sampling site.

	- raster_file (str): Path to the raster file of E as distributed by Chave.

	- e_value (float): Value of coefficient E.

	"""
	AGB = None
	if GDAL and longitude and latitude and raster_file and e_value is None:
		e_value = getE(longitude, latitude, raster_file)

	if isinstance(e_value, float) or isinstance(e_value, int):
		AGB = np.exp(-1.803 - 0.976 * e_value + 0.976 * np.log(density) + 2.673 * np.log(diameter) - 0.0299 * np.log(diameter)**2)

	return AGB


def det_vol(diams, length, tilts = None):
	"""
	Estimates volumen of detrites per unit area (m^3 / ha).

	Arguments:

	- diams (iterable): Diameter measurements, one by wood piece (cm).

	- length (float): Distance measurements were done upon (m).

	- tilts (iterable): Slope angles of pieces (degrees). It is recommended to
	exclude values greater than 85 degrees.

	"""

	vol = 0

	if tilts and len(diams) == len(tilts):
		for d,t in zip(diams, tilts):
			vol += d ** 2 / np.cos(np.radians(t))
	else:
		for d in diams:
			vol += d ** 2

	vol *= (np.pi**2 / 8)

	return vol


def det_density(dens, diams, length, tilts = None):
	"""
	Estimates detrite wood density per unit area [gr / (cm^3 * ha)].

	Arguments:

	- dens (iterable): Wood densities, one value per piece (gr/cm^3)

	- diams (iterable): Diameter measurements, one by wood piece (cm).

	- length (float): Distance measurements were done upon (m).

	- tilts (iterable): Slope angles of pieces (degrees). It is recommended to
	exclude values greater than 85 degrees.

	"""

	vol = 0
	vols = []
	dens_weighted = []

	if tilts and len(diams) == len(tilts):
		for d,t in zip(diams, tilts):
			this_vol = d ** 2 / np.cos(np.radians(t))
			vols.append(this_vol)
			vol += this_vol
	else:
		for d in diams:
			this_vol = d ** 2
			vols.append(this_vol)
			vol += this_vol

	dens_weighted = [d * (v / vol) for d,v in zip(dens, vols)]

	return sum(dens_weighted)
