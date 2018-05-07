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
	 
areas = {'Amazonia: Bosque': 39927789,
	'Amazonia: No-bosque': 5929583,
	'Andes: Bosque': 10727725,
	'Andes: No-bosque': 18468341,
	'Caribe: Bosque': 1773491,
	'Caribe: No-bosque': 13676394,
	'Orinoquia: Bosque': 2185583,
	'Orinoquia: No-bosque': 14646741,
	'Pacifico: Bosque': 5397941,
	'Pacifico: No-bosque': 1323911}

def domain_mean(dtfr, domain, variable, areas = areas):
	tot = 0.0
	for h in areas:
		if dtfr[(dtfr.Stratum == h) & (dtfr.Domain == domain)].shape[0] > 0:
			sum_y = dtfr.loc[(dtfr.Stratum == h) & (dtfr.Domain == domain), variable].sum()
			sum_a = float(dtfr.loc[(dtfr.Stratum == h), "Area"].sum())
			str_mean = sum_y / sum_a
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

		if dtfr[(dtfr.Stratum == h)].shape[0] > 1:

			n_h = float(dtfr[dtfr.Stratum == h].shape[0])
			fact = n_h ** 2 / (n_h - 1)
			
			A = sum(dtfr.loc[(dtfr.Stratum == h) & (dtfr.Domain == domain), variable] ** 2)		
			B = sum(dtfr.loc[(dtfr.Stratum == h) & (dtfr.Domain == domain), variable] * dtfr.loc[(dtfr.Stratum == h) & (dtfr.Domain == domain), 'Area'])
			C = sum(dtfr.loc[(dtfr.Stratum == h), 'Area'] ** 2)
			
			sum_y = 0.0
			if dtfr[(dtfr.Stratum == h) & (dtfr.Domain == domain)].shape[0] > 0:
				sum_y = dtfr.loc[(dtfr.Stratum == h) & (dtfr.Domain == domain), variable].sum()	
			sum_a = dtfr.loc[(dtfr.Stratum == h), "Area"].sum()
			
			str_mean = sum_y / float(sum_a)
			
			num = A - 2 * str_mean * B + str_mean ** 2 * C
			den = dtfr.loc[(dtfr.Stratum == h), 'Area'].sum() ** 2
			
			s2[h] = fact * num / float(den)
			
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
	sv = {}
	left = 0.0
	right = 0.0
	
	mean = domain_mean(dtfr, domain, variable, myareas)

	for h in strata_variances:
		
		sv[h] = 1.0 / (N - 1)
		
		sum_y = 0.0
		if dtfr[(dtfr.Stratum == h) & (dtfr.Domain == domain)].shape[0] > 1:
			sum_y = dtfr.loc[(dtfr.Stratum == h) & (dtfr.Domain == domain), variable].sum()
			
		sum_a = dtfr.loc[(dtfr.Stratum == h), "Area"].sum()
		str_mean = sum_y / float(sum_a)
		
		right = strata_weights[h] * (mean - str_mean) ** 2
				
		if map_strata_points[h] > 0:
	
			
			left = strata_weights[h] * strata_variances[h] * float(map_strata_points[h] - 1) \
				/ (float(dtfr[dtfr.Stratum == h].shape[0]) * (N - 1))
				
		else:
			left = 0.0
	
		sv[h] *= right
		sv[h] += left
	
	return sv	
	
def double_post_stratified_mean_var(dtfr, domain,  variable, strata_variances, strata_weights, map_strata_points, myareas):
	
	sv = {}
	
	N = float(sum(map_strata_points.values()))
	
	mean = domain_mean(dtfr, domain, variable, myareas)
	
	for h in strata_variances:
		sv[h] = 1.0 / (N - 1)
		left = 0.0
		center = 0.0
		right = 0.0
	
		sum_y = 0.0
		if dtfr[(dtfr.Stratum == h) & (dtfr.Domain == domain)].shape[0] > 1:
			sum_y = dtfr.loc[(dtfr.Stratum == h) & (dtfr.Domain == domain), variable].sum()
			
		sum_a = dtfr.loc[(dtfr.Stratum == h), "Area"].sum()
		str_mean = sum_y / sum_a
		
		left = (map_strata_points[h] - 1) * strata_variances[h] \
			/ ((N - 1) * float(dtfr.shape[0]))

		center = (1 - strata_weights[h]) * strata_variances[h] \
			/ dtfr.shape[0] ** 2
		
		right = (map_strata_points[h] / N) * (mean - str_mean) ** 2

		sv[h] *= right
		sv[h] += left + center
	
	return sv	
	

def cov_strata(dtfr, domain, domain_p,  var_y, var_x ):
	"""
	domain is subset of domain_p.
	"""
	covs = {}
	
	for h in dtfr.Stratum.unique().tolist():
		
		indxs = dtfr[((dtfr.Domain == domain) | (dtfr.Domain == domain_p)) & (dtfr.Stratum == h)].index
	
		if dtfr[dtfr.Stratum == h].shape[0] > 1:
		
			n_h = float(dtfr[(dtfr.Stratum == h)].shape[0])
			
			sum_y = 0.0
			if dtfr[(dtfr.Stratum == h) & (dtfr.Domain == domain)].shape[0] > 0:
				sum_y = dtfr.loc[(dtfr.Stratum == h) & (dtfr.Domain == domain), var_y].sum()
				
			sum_a = dtfr.loc[(dtfr.Stratum == h), "Area"].sum()
			mean_y = sum_y / sum_a
			
			sum_x = 0.0
			if dtfr[(dtfr.Stratum == h) & (dtfr.Domain == domain_p)].shape[0] > 0:
				sum_x = dtfr.loc[(dtfr.Stratum == h) & (dtfr.Domain == domain_p), var_x].sum()
				
			mean_x = sum_x / sum_a
			
			A = sum(dtfr.loc[indxs, var_y] * dtfr.loc[indxs, var_x])
			B = mean_y * sum(dtfr.loc[(dtfr.Stratum == h) & (dtfr.Domain == domain_p), "Area"] * dtfr.loc[(dtfr.Stratum == h) & (dtfr.Domain == domain_p), var_x])
			C =  mean_x * sum(dtfr.loc[(dtfr.Stratum == h) & (dtfr.Domain == domain), "Area"] * dtfr.loc[(dtfr.Stratum == h) & (dtfr.Domain == domain), var_y])
			D = sum(dtfr.loc[dtfr.Stratum == h, "Area"] ** 2) * mean_y * mean_x
			
			num = A - B - C + D
			den = dtfr.loc[dtfr.Stratum == h, "Area"].sum() ** 2
			
			covs[h] = (n_h ** 2 / (n_h - 1)) * (num / den)
		
		else:
			covs[h] = 0.0
			
	return covs


def cov_simple_stratified(dtfr, domain, domain_p,  var_y, var_x, strata_weights, myareas ):
	tcov = 0.0
	covs = cov_strata(dtfr, domain, domain_p,  var_y, var_x )
	
	for h in strata_weights:
		
		if dtfr[dtfr.Stratum == h].shape[0] > 0:
			tcov_h = strata_weights[h] ** 2 * covs[h] / dtfr[dtfr.Stratum == h].shape[0]
		else:
			tcov_h = 0.0
		
		tcov += tcov_h
		
	# Chip's formula doesn't have the exponential
	tcov *= sum(myareas.values()) ** 2
	
	return tcov
	
	
def cov_simple_post_stratified(dtfr, domain, domain_p,  var_y, var_x, strata_weights, myareas ):
	tcov = 0.0
	covs = cov_strata(dtfr, domain, domain_p,  var_y, var_x )
	
	for h in strata_weights:
		if dtfr[dtfr.Stratum == h].shape[0] > 0:
			tcov_h = (1 / float(dtfr.shape[0])) * ((strata_weights[h] * covs[h]) + ((1 - strata_weights[h]) * covs[h] / float(dtfr.shape[0])))
		else:
			tcov_h = 0.0
			
		tcov += tcov_h
		
	# Chip's formula doesn't have the exponential
	tcov *= sum(myareas.values()) ** 2
	
	return tcov
	

def cov_double_stratified(dtfr, domain, domain_p,  var_y, var_x, strata_weights, myareas, map_strata_points):
	tcov = 0.0
	covs = cov_strata(dtfr, domain, domain_p,  var_y, var_x )
	tot_points = float(sum(map_strata_points.values()))	
	mean_y = domain_mean(dtfr, domain, var_y, myareas)	
	mean_x = domain_mean(dtfr, domain_p, var_x, myareas)
	
	for h in strata_weights:
		if dtfr[dtfr.Stratum == h].shape[0] > 0:
			n_h = float(dtfr[dtfr.Stratum == h].shape[0])
			
			sum_y = 0.0
			if dtfr[(dtfr.Stratum == h) & (dtfr.Domain == domain)].shape[0] > 0:
				sum_y = dtfr.loc[(dtfr.Stratum == h) & (dtfr.Domain == domain), var_y].sum()
				
			sum_a = dtfr.loc[(dtfr.Stratum == h), "Area"].sum()
			mean_hy = sum_y / sum_a
			
			sum_x = 0.0
			if dtfr[(dtfr.Stratum == h) & (dtfr.Domain == domain_p)].shape[0] > 0:
				sum_x = dtfr.loc[(dtfr.Stratum == h) & (dtfr.Domain == domain_p), var_x].sum()
				
			mean_hx = sum_x / sum_a

			tcov_h = strata_weights[h] * (map_strata_points[h] - 1) / (tot_points - 1) * covs[h] / n_h
			tcov += 1 / (tot_points - 1) * strata_weights[h] * (mean_hy - mean_y) * (mean_hx - mean_x)
		else:
			tcov_h = 0.0
			
		tcov += tcov_h
		
	tcov *= sum(myareas.values()) ** 2
	
	return tcov
	
	
def cov_double_post_stratified(dtfr, domain, domain_p,  var_y, var_x, strata_weights, myareas, map_strata_points):
	tcov = 0.0
	covs = cov_strata(dtfr, domain, domain_p,  var_y, var_x )
	tot_points = float(sum(map_strata_points.values()))
	mean_y = domain_mean(dtfr, domain, var_y, myareas)
	mean_x = domain_mean(dtfr, domain_p, var_x, myareas)
	
	for h in strata_weights:
		if dtfr[dtfr.Stratum == h].shape[0] > 0:
			n_h = float(dtfr[dtfr.Stratum == h].shape[0])
			
			sum_y = 0.0
			if dtfr[(dtfr.Stratum == h) & (dtfr.Domain == domain)].shape[0] > 0:
				sum_y = dtfr.loc[(dtfr.Stratum == h) & (dtfr.Domain == domain), var_y].sum()
				
			sum_a = dtfr.loc[(dtfr.Stratum == h), "Area"].sum()
			mean_hy = sum_y / sum_a
			
			sum_x = 0.0
			if dtfr[(dtfr.Stratum == h) & (dtfr.Domain == domain_p)].shape[0] > 0:
				sum_x = dtfr.loc[(dtfr.Stratum == h) & (dtfr.Domain == domain_p), var_x].sum()
				
			mean_hx = sum_x / sum_a
			l = (map_strata_points[h] - 1) / (tot_points - 1) * covs[h] / float(dtfr.shape[0])
			c = (1 - strata_weights[h]) *  covs[h] / float(dtfr.shape[0]) ** 2
			r = 1 / (tot_points - 1) * strata_weights[h] * (mean_hy - mean_y) * (mean_hx - mean_x)
			tcov_h = l + c + r

		else:
			tcov_h = 0.0

		print tcov_h
		tcov += tcov_h
		
	tcov *= sum(myareas.values()) ** 2
	
	return tcov
