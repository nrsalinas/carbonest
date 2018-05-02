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

def strata_w(dtfr):
	w = {}
	for h in dtfr.Stratum.unique():
		w[h] = dtfr[dtfr.Stratum == h].shape[0] / float(dtfr.shape[0])
	return w

def strata_var(dtfr, domain,  variable):
	
	s2 = {}
	n = float(dtfr.shape[0])
	
	for h in dtfr.Stratum.unique():

		if dtfr[(dtfr.Stratum == h) & (dtfr.Domain == domain)].shape[0] > 1:

			fact = n / (float(dtfr[dtfr.Stratum == h].shape[0]) - 1)
			
			A = sum(dtfr.loc[(dtfr.Stratum == h) & (dtfr.Domain == domain), variable] ** 2)		
			B = sum(dtfr.loc[(dtfr.Stratum == h) & (dtfr.Domain == domain), variable] * dtfr.loc[(dtfr.Stratum == h) & (dtfr.Domain == domain), 'Area'])
			C = sum(dtfr.loc[(dtfr.Stratum == h) & (dtfr.Domain == domain), 'Area'] ** 2)
			
			str_mean = dtfr.loc[(dtfr.Stratum == h) & (dtfr.Domain == domain), variable].mean()
			
			num = A - 2 * str_mean * B + str_mean ** 2 * C
			den = dtfr.loc[(dtfr.Stratum == h) & (dtfr.Domain == domain), 'Area'].sum() ** 2
			
			s2[h] = fact * num / den
			
		else:
			s2[h] = 0
		
	return s2

def stratified_mean_var(dtfr, strata_variances, strata_weights):
	
	sv = 0.0
	for h in strata_variances:
		sv += (strata_weights[h] ** 2 * strata_variances[h]) / (strata_weights[h] * dtfr.shape[0])
	
	return sv	
	
def post_stratified_mean_var(dtfr, strata_variances, strata_weights):
	
	pv = 0.0
	for h in strata_variances:
		pv += strata_weights[h] ** 2 * strata_variances[h] 
		pv += ((strata_weights[h] - 1) * strata_variances[h]) / dtfr.shape[0]
	
	return pv / dtfr.shape[0]

def double_stratified_mean_var(dtfr, domain,  variable, strata_variances, strata_weights, map_strata_points):
	N = float(sum(map_strata_points.values()))
	sv = 1.0 / (N - 1)
	left = 0.0
	right = 0.0
	
	#mean = dtfr.loc[(dtfr.Domain == domain), variable].sum() / dtfr.shape[0]
	mean = 0.0
	for h in strata_weights:
		mean += dtfr.loc[(dtfr.Domain == domain) & (dtfr.Stratum == h), variable].mean() * strata_weights[h]
	
	for h in strata_variances:
		
		if dtfr[(dtfr.Stratum == h)].shape[0] > 1 and map_strata_points[h] > 1 \
			and strata_variances[h] > 0: 
		
			str_mean = dtfr.loc[(dtfr.Domain == domain) & (dtfr.Stratum == h), variable].mean()
			
			left += (map_strata_points[h] / N) * strata_variances[h] * (map_strata_points[h] - 1) \
				/ ((dtfr.shape[0] * strata_weights[h]) * (N - 1))
			
			right += (map_strata_points[h] / N) * (mean - str_mean) ** 2
					
	sv *= right
	sv += left
	
	return sv	
	
def double_post_stratified_mean_var(dtfr, domain,  variable, strata_variances, strata_weights, map_strata_points):
	N = float(sum(map_strata_points.values()))
	sv = 1.0 / (N - 1)
	left = 0.0
	center = 0.0
	right = 0.0
	
	#mean = dtfr.loc[(dtfr.Domain == domain), variable].mean()
	mean = 0.0
	for h in strata_weights:
		mean += dtfr.loc[(dtfr.Domain == domain) & (dtfr.Stratum == h), variable].mean() * strata_weights[h]
	
	for h in strata_variances:
		
		if dtfr[(dtfr.Stratum == h)].shape[0] > 1 and map_strata_points[h] > 1 \
			and strata_variances[h] > 0: 
		
			mean_h = dtfr.loc[(dtfr.Domain == domain) & (dtfr.Stratum == h), variable].mean()
			
			left += strata_variances[h] * (map_strata_points[h] - 1) \
				/ (float(dtfr.shape[0]) * (N - 1))
			
			center += (1 - (map_strata_points[h] / N)) * strata_variances[h] \
				/ dtfr.shape[0] ** 2

			right += (map_strata_points[h] / N) * (mean - mean_h) ** 2
					
	sv *= right
	sv += left + center
	
	return sv	
	

def cov_strata(dtfr, domain, domain_p,  var_y, var_x ):
	"""
	domain is subset of domain_p.
	"""
	covs = {}
	
	for h in dtfr.Stratum.unique():
		
		indxs = dtfr[((dtfr.Domain == domain) | (dtfr.Domain == domain_p)) & (dtfr.Stratum == h)].index
	
		if len(indxs) > 1:
		
			n_h = float(dtfr[(dtfr.Domain == domain) & (dtfr.Stratum == h)].shape[0])
			
			mean_y = dtfr.loc[indxs, var_y].mean()
			mean_x = dtfr.loc[indxs, var_x].mean()
			
			num = sum((dtfr.loc[indxs, var_y] - (dtfr.loc[indxs, "Area"] * mean_y)) * (dtfr.loc[indxs, var_x] - (dtfr.loc[indxs, "Area"] * mean_x)))
			
			den = (dtfr["Area"].sum()) ** 2
			
			covs[h] = (n_h / (n_h - 1)) * (num / den)
		
		else:
			covs[h] = 0.0
			
	return covs


def cov_strata_total(dtfr, domain, domain_p,  var_y, var_x, strata_weights ):
	tcov = 0.0
	covs = cov_strata(dtfr, domain, domain_p,  var_y, var_x )
	
	for h in strata_weights:
		tcov = strata_weights[h] ** 2 * covs[h] / dtfr[dtfr.Stratum == h].shape[0]
	
	tcov *= (dtfr["Area"].sum()) ** 2
	
	return tcov
	
	
	
	
	
	
	
	
	
	
	
