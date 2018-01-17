import gdal
import numpy as np
import allometry
import pickle

alt_file = "/home/nelsonsalinas/Documents/cust_layers/alt/vent_alt.tif"

prec_file = "/home/nelsonsalinas/Documents/cust_layers/precp/precp.tif"

#for_file = "/home/nelsonsalinas/Documents/Cartografia_SIAC/bosque_no_bosque_2016/BQNBQ_2016_EPSG4326.tif"
for_file = "/home/nelsonsalinas/Documents/Cartografia_SIAC/bosque_no_bosque_2015/BQNBQ_2015_EPSG4326.tif"

alt_ras = gdal.Open(alt_file)
prec_ras = gdal.Open(prec_file)

for_ras = gdal.Open(for_file)

transform = alt_ras.GetGeoTransform()
altXOrigin = transform[0]
altYOrigin = transform[3]
altPixelWidth = transform[1]
altPixelHeight = transform[5]

transform = for_ras.GetGeoTransform()
forXOrigin = transform[0]
forYOrigin = transform[3]
forPixelWidth = transform[1]
forPixelHeight = transform[5]

for_band = for_ras.GetRasterBand(1)

#for_band = for_ras.GetRasterBand(1)

#for_arr = for_band.ReadAsArray(0,0,for_ras.RasterXSize, for_ras.RasterYSize)

alt_band = alt_ras.GetRasterBand(1)
alt_arr = alt_band.ReadAsArray(0,0,alt_ras.RasterXSize, alt_ras.RasterYSize)

prec_band = prec_ras.GetRasterBand(1)
prec_arr = prec_band.ReadAsArray(0,0,prec_ras.RasterXSize, prec_ras.RasterYSize)

for_type_count ={'holdrigde':{}, 'chaveI':{}}


it = np.nditer((alt_arr, prec_arr), flags=['multi_index'])
while not it.finished:
	if it[0] >= 0 and it[1] > 0:
		holdr = allometry.holdridge_col(it[0], it[1])
		chave = allometry.chaveI_forest(it[1])

		if holdr and chave:
			row = it.multi_index[0]
			col = it.multi_index[1]
			lon = col * altPixelWidth + altXOrigin
			lat = row * altPixelHeight + altYOrigin

			if lon >= forXOrigin and lat <= forYOrigin:
				fpx = int((lon - forXOrigin) / forPixelWidth)
				fpy = int((lat - forYOrigin) / forPixelHeight)

				if fpx <= for_ras.RasterXSize and fpy <= for_ras.RasterYSize:
					for_val = for_band.ReadAsArray(fpx, fpy, 1, 1)

					if for_val and for_val[0][0] == 1:

						if not holdr in for_type_count['holdrigde']:
							for_type_count['holdrigde'][holdr] = 1
						else:
							for_type_count['holdrigde'][holdr] += 1
						if not chave in for_type_count['chaveI']:
							for_type_count['chaveI'][chave] = 1
						else:
							for_type_count['chaveI'][chave] += 1
	it.iternext()

pickle.dump(for_type_count, open("for_pix_count.pkl","w"))
