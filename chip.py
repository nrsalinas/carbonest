# Muestro estratificado aleatorio

# Estructura de datos base es un dataframe con los datos de estimacion de biomasa 
# por conglomerado. Columnas especificas:
# Estrato_mapa: Codificacion de estrato dado por cartografia
# Estrato_campo: Estrato observado en campo 

# Pesos estratos
# Codigos:
# 1 = bosque
# 2 = no bosque
# 3 = nan

weights = {'Amazonia: Bosque': 0.3501,
	'Amazonia: No-bosque': 0.0520,
	'Andes: Bosque': 0.0941,
	'Andes: No-bosque': 0.1619,
	'Caribe: Bosque': 0.0155,
	'Caribe: No-bosque': 0.1199,
	'Orinoquia: Bosque': 0.0192,
	'Orinoquia: No-bosque': 0.1284,
	'Pacifico: Bosque': 0.0473,
	'Pacifico: No-bosque': 0.0116}
 
map_points = {
	"Amazonia: Bosque": 7000,
	"Amazonia: No-bosque": 1000,
	"Andes: Bosque": 1800,
	"Andes: No-bosque": 3200,
	"Caribe: Bosque": 400,
	"Caribe: No-bosque": 2400,
	"Orinoquia: Bosque": 400,
	"Orinoquia: No-bosque": 2600,
	"Pacifico: Bosque": 1000,
	"Pacifico: No-bosque": 200
	 }
	 
areas_chip = {'Amazonia: Bosque': 39927789,
	'Amazonia: No-bosque': 5929583,
	'Andes: Bosque': 10727725,
	'Andes: No-bosque': 18468341,
	'Caribe: Bosque': 1773491,
	'Caribe: No-bosque': 13676394,
	'Orinoquia: Bosque': 2185583,
	'Orinoquia: No-bosque': 14646741,
	'Pacifico: Bosque': 5397941,
	'Pacifico: No-bosque': 1323911}

def domain_mean(dtfr, domain, variable, areas = areas_chip):
	tot = 0.0
	for h in areas:
		if dtfr[(dtfr.Stratum == h) & (dtfr.Domain == domain)].shape[0] > 0:
			sum_y = dtfr.loc[(dtfr.Stratum == h) & (dtfr.Domain == domain), variable].sum()
			#print sum_y
			sum_a = float(dtfr.loc[(dtfr.Stratum == h), "Area"].sum())
			#print sum_a
			str_mean = sum_y / sum_a
			#print str_mean
			tot += str_mean * areas[h]
	tot /= sum(areas.values())
	return tot

def strata_w(dtfr):
	w = {}
	for h in dtfr.Stratum.unique():
		w[h] = dtfr[dtfr.Stratum == h].shape[0] / float(dtfr.shape[0])
	return w

def strata_var(dtfr, domain,  variable):
	
	s2 = {}
		
	for h in dtfr.Stratum.unique():

		#print "\n", h

		if dtfr[(dtfr.Stratum == h)].shape[0] > 1:

			n_h = float(dtfr[dtfr.Stratum == h].shape[0])
			fact = n_h ** 2 / (n_h - 1)
			#print "n_h:", n_h
			
			A = sum(dtfr.loc[(dtfr.Stratum == h) & (dtfr.Domain == domain), variable] ** 2)		
			#print "A:",A
			B = sum(dtfr.loc[(dtfr.Stratum == h) & (dtfr.Domain == domain), variable] * dtfr.loc[(dtfr.Stratum == h) & (dtfr.Domain == domain), 'Area'])
			#print "B:", B
			C = sum(dtfr.loc[(dtfr.Stratum == h), 'Area'] ** 2)
			#print "C:", C
			
			sum_y = 0.0
			if dtfr[(dtfr.Stratum == h) & (dtfr.Domain == domain)].shape[0] > 0:
				sum_y = dtfr.loc[(dtfr.Stratum == h) & (dtfr.Domain == domain), variable].sum()	
			sum_a = dtfr.loc[(dtfr.Stratum == h), "Area"].sum()
			#print "sum_y:", sum_y
			#print "sum_a:", sum_a
			str_mean = sum_y / sum_a
			#print "str_mean:", str_mean
			
			num = A - 2 * str_mean * B + str_mean ** 2 * C
			den = dtfr.loc[(dtfr.Stratum == h), 'Area'].sum() ** 2
			#print "AM:", den ** 0.5
			
			s2[h] = fact * num / den
			
		else:
			s2[h] = 0
		
	return s2

def stratified_mean_var(dtfr, strata_variances, strata_weights):
	
	sv = {}
	for h in strata_variances:
		sv[h] = (strata_weights[h] ** 2 * strata_variances[h]) / dtfr[dtfr.Stratum == h].shape[0]
	
	return sv	
	
def post_stratified_mean_var(dtfr, strata_variances, strata_weights):
	
	pv = {}
	for h in strata_variances:
		pv[h] = strata_weights[h] * strata_variances[h] 
		pv[h] += ((1 - strata_weights[h]) * strata_variances[h]) / dtfr.shape[0]
		pv[h] /= dtfr.shape[0]

	return pv

def double_stratified_mean_var(dtfr, domain,  variable, strata_variances, strata_weights, map_strata_points, myareas):
	
	N = float(sum(map_strata_points.values()))
	#print "N:", N
	#sv = 1.0 / (N - 1)
	sv = {}
	left = 0.0
	right = 0.0
	
	#mean = dtfr.loc[(dtfr.Domain == domain), variable].sum() / dtfr.shape[0]
	mean = domain_mean(dtfr, domain, variable, myareas)

	#print "mean:", mean
	
	for h in strata_variances:
		
		#print "\n",h
		sv[h] = 1.0 / (N - 1)
		
		sum_y = 0.0
		if dtfr[(dtfr.Stratum == h) & (dtfr.Domain == domain)].shape[0] > 1:
			sum_y = dtfr.loc[(dtfr.Stratum == h) & (dtfr.Domain == domain), variable].sum()
			
		sum_a = dtfr.loc[(dtfr.Stratum == h), "Area"].sum()
		#print "sum_y:", sum_y
		#print "sum_a:", sum_a
		str_mean = sum_y / sum_a
		
		#print "str_mean:", str_mean

		right = (map_strata_points[h] / N) * (mean - str_mean) ** 2
				
		#print "right:", right
		
		#if dtfr[(dtfr.Stratum == h)].shape[0] > 0 and map_strata_points[h] > 0 and strata_variances[h] > 0: 
		if map_strata_points[h] > 0:
	
			
			left = (map_strata_points[h] / N) * strata_variances[h] * (map_strata_points[h] - 1) \
				/ (float(dtfr[dtfr.Stratum == h].shape[0]) * (N - 1))
				
			#print "left:", left
			#print "AG6:", (map_strata_points[h] / N)
			#print "AF6:", map_strata_points[h]
			#print "AN6:", strata_variances[h]
			#print "AF17:", N
			#print "AE6:" , float(dtfr[dtfr.Stratum == h].shape[0])
			
		else:
			left = 0.0
	
		sv[h] *= right
		sv[h] += left
	
	return sv	
	
def double_post_stratified_mean_var(dtfr, domain,  variable, strata_variances, strata_weights, map_strata_points, myareas):
	
	sv = {}
	
	N = float(sum(map_strata_points.values()))
	
	#mean = dtfr.loc[(dtfr.Domain == domain), variable].mean()
	#mean = 0.0
	#for h in strata_weights:
	#	mean += dtfr.loc[(dtfr.Domain == domain) & (dtfr.Stratum == h), variable].mean() * strata_weights[h]
	mean = domain_mean(dtfr, domain, variable, myareas)
	
	for h in strata_variances:
		#print "\n", h
		sv[h] = 1.0 / (N - 1)
		left = 0.0
		center = 0.0
		right = 0.0
	
		#if dtfr[(dtfr.Stratum == h)].shape[0] > 1 and map_strata_points[h] > 1 and strata_variances[h] > 0: 
		
		sum_y = 0.0
		if dtfr[(dtfr.Stratum == h) & (dtfr.Domain == domain)].shape[0] > 1:
			sum_y = dtfr.loc[(dtfr.Stratum == h) & (dtfr.Domain == domain), variable].sum()
			
		sum_a = dtfr.loc[(dtfr.Stratum == h), "Area"].sum()
		#print "sum_y:", sum_y
		#print "sum_a:", sum_a
		str_mean = sum_y / sum_a
		
		left = (map_strata_points[h] - 1) * strata_variances[h] \
			/ ((N - 1) * float(dtfr.shape[0]))
		"""
		print "AF:", map_strata_points[h]
		print "AF17:", N
		print "AN:", strata_variances[h]
		print "AE17:", dtfr.shape[0]
		"""
		#print "left:", left

		center = (1 - (map_strata_points[h] / N)) * strata_variances[h] \
			/ dtfr.shape[0] ** 2
		#print "center:",center
		
		right = (map_strata_points[h] / N) * (mean - str_mean) ** 2
		"""
		print "AG:", (map_strata_points[h] / N)
		print "AH:", str_mean
		print "AJ19:" , mean
		"""
		#print "right:", right


		sv[h] *= right
		sv[h] += left + center
	
	return sv	
	

def cov_strata(dtfr, domain, domain_p,  var_y, var_x ):
	"""
	domain is subset of domain_p.
	"""
	covs = {}
	
	for h in dtfr.Stratum.unique().tolist():
		
		#print "\n",h
		indxs = dtfr[((dtfr.Domain == domain) | (dtfr.Domain == domain_p)) & (dtfr.Stratum == h)].index
	
		if dtfr[dtfr.Stratum == h].shape[0] > 1:
		
			n_h = float(dtfr[(dtfr.Stratum == h)].shape[0])
			
			#mean_y = dtfr.loc[indxs, var_y].mean()
			sum_y = 0.0
			if dtfr[(dtfr.Stratum == h) & (dtfr.Domain == domain)].shape[0] > 0:
				sum_y = dtfr.loc[(dtfr.Stratum == h) & (dtfr.Domain == domain), var_y].sum()
				
			sum_a = dtfr.loc[(dtfr.Stratum == h), "Area"].sum()
			#print "sum_y:", sum_y
			#print "sum_a:", sum_a
			mean_y = sum_y / sum_a
			
			#print "mean_y:",mean_y
			
			#mean_x = dtfr.loc[indxs, var_x].mean()
			sum_x = 0.0
			if dtfr[(dtfr.Stratum == h) & (dtfr.Domain == domain_p)].shape[0] > 0:
				sum_x = dtfr.loc[(dtfr.Stratum == h) & (dtfr.Domain == domain_p), var_x].sum()
				
			#sum_a = dtfr.loc[(dtfr.Stratum == h), "Area"].sum()
			#print "sum_y:", sum_y
			#print "sum_a:", sum_a
			mean_x = sum_x / sum_a
			#print "mean_x:",mean_x
			
			#num = sum((dtfr.loc[indxs, var_y] - (dtfr.loc[indxs, "Area"] * mean_y)) * (dtfr.loc[indxs, var_x] - (dtfr.loc[indxs, "Area"] * mean_x)))
			A = sum(dtfr.loc[indxs, var_y] * dtfr.loc[indxs, var_x])
			#print "A:",A
			
			B = mean_y * sum(dtfr.loc[(dtfr.Stratum == h) & (dtfr.Domain == domain_p), "Area"] * dtfr.loc[(dtfr.Stratum == h) & (dtfr.Domain == domain_p), var_x])
			#print "B:", B
			
			C =  mean_x * sum(dtfr.loc[(dtfr.Stratum == h) & (dtfr.Domain == domain), "Area"] * dtfr.loc[(dtfr.Stratum == h) & (dtfr.Domain == domain), var_y])
			#print "C:", C
			
			D = sum(dtfr.loc[dtfr.Stratum == h, "Area"] ** 2) * mean_y * mean_x
			#print "D:", D

			num = A - B - C + D
			den = (dtfr.loc[dtfr.Stratum == h, "Area"].sum()) ** 2
			#print "den:", den
			#print "fact:", (n_h ** 2 / (n_h - 1))
			
			covs[h] = (n_h ** 2 / (n_h - 1)) * (num / den)
		
		else:
			covs[h] = 0.0
			
	return covs


def cov_simple_stratified(dtfr, domain, domain_p,  var_y, var_x, strata_weights, myareas ):
	tcov = 0.0
	covs = cov_strata(dtfr, domain, domain_p,  var_y, var_x )
	
	for h in strata_weights:
		print "\n",h
		tcov_h = strata_weights[h] ** 2 * covs[h] / dtfr[dtfr.Stratum == h].shape[0]
		print tcov_h
		tcov += tcov
		
	# Chip's formula doesn't have the exponential
	tcov *= sum(myareas.values()) ** 2
	
	return tcov
	
	
def cov_simple_post_stratified(dtfr, domain, domain_p,  var_y, var_x, strata_weights, myareas ):
	tcov = 0.0
	covs = cov_strata(dtfr, domain, domain_p,  var_y, var_x )
	
	for h in strata_weights:
		print "\n",h
		print "n:", dtfr.shape[0]
		print "w:", strata_weights[h]
		print "strata covariance:", covs[h]
		tcov_h = (1 / float(dtfr.shape[0])) * ((strata_weights[h] * covs[h]) + ((1 - strata_weights[h]) * covs[h] / float(dtfr.shape[0])))
		print tcov_h
		tcov += tcov
		
	# Chip's formula doesn't have the exponential
	tcov *= sum(myareas.values()) ** 2
	
	return tcov
	
	
	
	
	
	
	
	
	
	
	
