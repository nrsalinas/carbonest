from pandas import DataFrame
from scipy.stats import t

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
	

class Estimator(object):
	
	def __init__(self, dtfr, areas, weights):
		
		if isinstance(dtfr, DataFrame):
			self.dtfr = dtfr
		
		self.areas = areas
		self.weights = weights
		self.s2 = None # Strata variances
		self.map_points = None
		self.covs = None
		
	
	def stratum_mean(self, stratum, domain, variable):
		sum_y = 0.0
		if self.dtfr[(self.dtfr.Stratum == stratum) & (self.dtfr.Domain == domain)].shape[0] > 0:
			sum_y = self.dtfr.loc[(self.dtfr.Stratum == stratum) & (self.dtfr.Domain == domain), variable].sum()
			
		sum_a = self.dtfr.loc[(self.dtfr.Stratum == stratum), "Area"].sum()
		str_mean = sum_y / float(sum_a)
		return str_mean

		
	def domain_mean(self, domain, variable):
		tot = 0.0
		
		for h in self.areas:
			tot += self.stratum_mean(h, domain, variable) * self.areas[h]
		
		tot /= sum(self.areas.values())
		
		return tot

		
	def total(self, domain, variable):
		tot = 0.0
		for h in self.dtfr.Stratum.unique():
			#print "\n",h
			str_mean = self.stratum_mean(h, domain, variable)
			#print str_mean
			tot += str_mean * self.areas[h]
			#print str_mean * self.areas[h]
		return tot
		
	
	def ratio(self, domain, domain_p, var_y, var_x):
		return self.total(domain, var_y) / self.total(domain_p, var_x)
		

	def var_total(self, var_dict):
		return sum(self.areas.values()) ** 2 * sum(var_dict.values())


	def get_strata_var(self, domain, variable):
		
		self.s2 = {}
			
		for h in self.dtfr.Stratum.unique():

			if self.dtfr[(self.dtfr.Stratum == h)].shape[0] > 1:

				n_h = float(self.dtfr[self.dtfr.Stratum == h].shape[0])
				fact = n_h ** 2 / (n_h - 1)
				
				A = sum(self.dtfr.loc[(self.dtfr.Stratum == h) & (self.dtfr.Domain == domain), variable] ** 2)		
				B = sum(self.dtfr.loc[(self.dtfr.Stratum == h) & (self.dtfr.Domain == domain), variable] * self.dtfr.loc[(self.dtfr.Stratum == h) & (self.dtfr.Domain == domain), 'Area'])
				C = sum(self.dtfr.loc[(self.dtfr.Stratum == h), 'Area'] ** 2)
				
				sum_y = 0.0
				if self.dtfr[(self.dtfr.Stratum == h) & (self.dtfr.Domain == domain)].shape[0] > 0:
					sum_y = self.dtfr.loc[(self.dtfr.Stratum == h) & (self.dtfr.Domain == domain), variable].sum()	
				sum_a = self.dtfr.loc[(self.dtfr.Stratum == h), "Area"].sum()
				
				str_mean = sum_y / float(sum_a)
				
				num = A - 2 * str_mean * B + str_mean ** 2 * C
				den = self.dtfr.loc[(self.dtfr.Stratum == h), 'Area'].sum() ** 2
				
				self.s2[h] = fact * num / float(den)
				
			else:
				self.s2[h] = 0
			
		return None
		
		
	def stratified_mean_var(self, domain, variable, confidence = 0.95):
		sv = {}
		self.get_strata_var(domain, variable)
			
		for h in self.s2:
			sv[h] = (self.weights[h] ** 2 * self.s2[h]) / self.dtfr[self.dtfr.Stratum == h].shape[0]
			
		vartot = self.var_total(sv)
		std_err = (vartot / self.dtfr.shape[0]) ** 0.5
		mean = self.dtfr.loc[self.dtfr.Domain == domain, variable].sum() / float(self.dtfr.shape[0])
		poptot = self.total(domain, variable) #sum(self.areas.values()) * mean
		rel_error = vartot ** 0.5 / self.total(domain, variable) * 100
		conf_inter = t.interval(confidence, self.dtfr.shape[0] - 1, poptot, std_err) 
		out = {'Domain mean': mean,
			'Population total': poptot,
			'Strata variances': sv, 
			'Variance of the total': vartot,
			'Relative error': rel_error,
			'Confidence interval': conf_inter}
		
		return out
		
	def post_stratified_mean_var(self, domain, variable, confidence = 0.95):
		pv = {}
		self.get_strata_var(domain, variable)
		
		for h in self.s2:
			pv[h] = self.weights[h] * self.s2[h] 
			pv[h] += ((1 - self.weights[h]) * self.s2[h]) / self.dtfr.shape[0]
			pv[h] /= self.dtfr.shape[0]

		vartot = self.var_total(pv)
		std_err = (vartot / self.dtfr.shape[0]) ** 0.5
		mean = self.dtfr.loc[self.dtfr.Domain == domain, variable].sum() / float(self.dtfr.shape[0])
		poptot = self.total(domain, variable) #sum(self.areas.values()) * mean
		rel_error = vartot ** 0.5 / self.total(domain, variable) * 100
		conf_inter = t.interval(confidence, self.dtfr.shape[0] - 1, poptot, std_err) 
		out = {'Domain mean': mean,
			'Population total': poptot,
			'Strata variances': pv, 
			'Variance of the total': vartot, 
			'Relative error': rel_error,
			'Confidence interval': conf_inter}

		return out


	def double_stratified_mean_var(self, domain,  variable, confidence = 0.95):
		
		self.get_strata_var(domain, variable)
		
		N = float(sum(self.map_points.values()))
		sv = {}
		left = 0.0
		right = 0.0
		
		mean = self.domain_mean(domain, variable)

		for h in self.s2:
			
			sv[h] = 1.0 / (N - 1)
			
			sum_y = 0.0
			if self.dtfr[(self.dtfr.Stratum == h) & (self.dtfr.Domain == domain)].shape[0] > 1:
				sum_y = self.dtfr.loc[(self.dtfr.Stratum == h) & (self.dtfr.Domain == domain), variable].sum()
				
			sum_a = self.dtfr.loc[(self.dtfr.Stratum == h), "Area"].sum()
			str_mean = sum_y / float(sum_a)
			
			right = self.weights[h] * (mean - str_mean) ** 2
					
			if self.map_points[h] > 0:
		
				
				left = self.weights[h] * self.s2[h] * float(self.map_points[h] - 1) \
					/ (float(self.dtfr[self.dtfr.Stratum == h].shape[0]) * (N - 1))
					
			else:
				left = 0.0
		
			sv[h] *= right
			sv[h] += left
		
		vartot = self.var_total(sv)
		std_err = (vartot / self.dtfr.shape[0]) ** 0.5
		mean = self.dtfr.loc[self.dtfr.Domain == domain, variable].sum() / float(self.dtfr.shape[0])
		poptot = self.total(domain, variable) #sum(self.areas.values()) * mean
		rel_error = vartot ** 0.5 / self.total(domain, variable) * 100
		conf_inter = t.interval(confidence, self.dtfr.shape[0] - 1, poptot, std_err) 
		out = {'Domain mean': mean,
			'Population total': poptot,
			'Strata variances': sv, 
			'Variance of the total': vartot,
			'Relative error': rel_error,
			'Confidence interval': conf_inter}
		
		return out	
		

	def double_post_stratified_mean_var(self, domain,  variable, confidence = 0.95):
		
		self.get_strata_var(domain, variable)
		sv = {}
		
		N = float(sum(self.map_points.values()))
		
		mean = self.domain_mean(domain, variable)
		
		for h in self.s2:
			sv[h] = 1.0 / (N - 1)
			left = 0.0
			center = 0.0
			right = 0.0
		
			sum_y = 0.0
			if self.dtfr[(self.dtfr.Stratum == h) & (self.dtfr.Domain == domain)].shape[0] > 1:
				sum_y = self.dtfr.loc[(self.dtfr.Stratum == h) & (self.dtfr.Domain == domain), variable].sum()
				
			sum_a = self.dtfr.loc[(self.dtfr.Stratum == h), "Area"].sum()
			str_mean = sum_y / sum_a
			
			left = (self.map_points[h] - 1) * self.s2[h] \
				/ ((N - 1) * float(self.dtfr.shape[0]))

			center = (1 - self.weights[h]) * self.s2[h] \
				/ self.dtfr.shape[0] ** 2
			
			right = (self.map_points[h] / N) * (mean - str_mean) ** 2

			sv[h] *= right
			sv[h] += left + center
		
		vartot = self.var_total(sv)
		std_err = (vartot / self.dtfr.shape[0]) ** 0.5
		mean = self.dtfr.loc[self.dtfr.Domain == domain, variable].sum() / float(self.dtfr.shape[0])
		poptot = self.total(domain, variable) #sum(self.areas.values()) * mean
		rel_error = vartot ** 0.5 / self.total(domain, variable) * 100
		conf_inter = t.interval(confidence, self.dtfr.shape[0] - 1, poptot, std_err) 
		out = {'Domain mean': mean,
			'Population total': poptot,
			'Strata variances': sv, 
			'Variance of the total': vartot,
			'Relative error': rel_error,
			'Confidence interval': conf_inter}
		
		return out	
	

	def get_cov_strata(self, domain, domain_p,  var_y, var_x ):
		"""
		`domain` is subset of `domain_p`.
		"""
		self.covs = {}
		
		for h in self.dtfr.Stratum.unique().tolist():
			
			indxs = self.dtfr[((self.dtfr.Domain == domain) | (self.dtfr.Domain == domain_p)) & (self.dtfr.Stratum == h)].index
		
			if self.dtfr[self.dtfr.Stratum == h].shape[0] > 1:
			
				n_h = float(self.dtfr[(self.dtfr.Stratum == h)].shape[0])
				
				sum_y = 0.0
				if self.dtfr[(self.dtfr.Stratum == h) & (self.dtfr.Domain == domain)].shape[0] > 0:
					sum_y = self.dtfr.loc[(self.dtfr.Stratum == h) & (self.dtfr.Domain == domain), var_y].sum()
					
				sum_a = self.dtfr.loc[(self.dtfr.Stratum == h), "Area"].sum()
				mean_y = sum_y / sum_a
				
				sum_x = 0.0
				if self.dtfr[(self.dtfr.Stratum == h) & (self.dtfr.Domain == domain_p)].shape[0] > 0:
					sum_x = self.dtfr.loc[(self.dtfr.Stratum == h) & (self.dtfr.Domain == domain_p), var_x].sum()
					
				mean_x = sum_x / sum_a
				
				A = sum(self.dtfr.loc[indxs, var_y] * self.dtfr.loc[indxs, var_x])
				B = mean_y * sum(self.dtfr.loc[(self.dtfr.Stratum == h) & (self.dtfr.Domain == domain_p), "Area"] * self.dtfr.loc[(self.dtfr.Stratum == h) & (self.dtfr.Domain == domain_p), var_x])
				C =  mean_x * sum(self.dtfr.loc[(self.dtfr.Stratum == h) & (self.dtfr.Domain == domain), "Area"] * self.dtfr.loc[(self.dtfr.Stratum == h) & (self.dtfr.Domain == domain), var_y])
				D = sum(self.dtfr.loc[self.dtfr.Stratum == h, "Area"] ** 2) * mean_y * mean_x
				
				num = A - B - C + D
				den = self.dtfr.loc[self.dtfr.Stratum == h, "Area"].sum() ** 2
				
				self.covs[h] = (n_h ** 2 / (n_h - 1)) * (num / den)
			
			else:
				self.covs[h] = 0.0
				
		return None
		
			
	def cov_stratified(self, domain, domain_p,  var_y, var_x):
		
		self.get_cov_strata(domain, domain_p,  var_y, var_x )
		tcov = 0.0
		
		for h in self.weights:
			
			if self.dtfr[self.dtfr.Stratum == h].shape[0] > 0:
				tcov_h = self.weights[h] ** 2 * self.covs[h] / self.dtfr[self.dtfr.Stratum == h].shape[0]
			else:
				tcov_h = 0.0
			
			tcov += tcov_h
			
		tcov *= sum(self.areas.values()) ** 2
		
		return tcov
		
		
	def cov_post_stratified(self, domain, domain_p, var_y, var_x):
		
		self.get_cov_strata(domain, domain_p,  var_y, var_x )
		tcov = 0.0
		for h in self.weights:
			if self.dtfr[self.dtfr.Stratum == h].shape[0] > 0:
				tcov_h = (1 / float(self.dtfr.shape[0])) * ((self.weights[h] * self.covs[h]) + ((1 - self.weights[h]) * self.covs[h] / float(self.dtfr.shape[0])))
			else:
				tcov_h = 0.0
				
			tcov += tcov_h
			
		# In Chip's formula the sum of the areas is not exponentiated
		tcov *= sum(self.areas.values()) ** 2
		
		return tcov
		
		
	def cov_double_stratified(self, domain, domain_p,  var_y, var_x):
		self.get_cov_strata(domain, domain_p,  var_y, var_x )
		tcov = 0.0

		tot_points = float(sum(self.map_points.values()))	
		mean_y = self.domain_mean(domain, var_y)	
		mean_x = self.domain_mean(domain_p, var_x)
		
		for h in self.weights:
			if self.dtfr[self.dtfr.Stratum == h].shape[0] > 0:
				n_h = float(self.dtfr[self.dtfr.Stratum == h].shape[0])
				
				sum_y = 0.0
				if self.dtfr[(self.dtfr.Stratum == h) & (self.dtfr.Domain == domain)].shape[0] > 0:
					sum_y = self.dtfr.loc[(self.dtfr.Stratum == h) & (self.dtfr.Domain == domain), var_y].sum()
					
				sum_a = self.dtfr.loc[(self.dtfr.Stratum == h), "Area"].sum()
				mean_hy = sum_y / sum_a
				
				sum_x = 0.0
				if self.dtfr[(self.dtfr.Stratum == h) & (self.dtfr.Domain == domain_p)].shape[0] > 0:
					sum_x = self.dtfr.loc[(self.dtfr.Stratum == h) & (self.dtfr.Domain == domain_p), var_x].sum()
					
				mean_hx = sum_x / sum_a

				tcov_h = self.weights[h] * (self.map_points[h] - 1) / (tot_points - 1) * self.covs[h] / n_h
				tcov += 1 / (tot_points - 1) * self.weights[h] * (mean_hy - mean_y) * (mean_hx - mean_x)
			else:
				tcov_h = 0.0
				
			tcov += tcov_h
			
		tcov *= sum(self.areas.values()) ** 2
		
		return tcov


	def cov_double_post_stratified(self, domain, domain_p,  var_y, var_x):
		tcov = 0.0
		self.get_cov_strata(domain, domain_p, var_y, var_x )
		tot_points = float(sum(self.map_points.values()))
		mean_y = self.domain_mean(domain, var_y)
		mean_x = self.domain_mean(domain_p, var_x)
		
		for h in self.weights:
			if self.dtfr[self.dtfr.Stratum == h].shape[0] > 0:
				n_h = float(self.dtfr[self.dtfr.Stratum == h].shape[0])
				
				sum_y = 0.0
				if self.dtfr[(self.dtfr.Stratum == h) & (self.dtfr.Domain == domain)].shape[0] > 0:
					sum_y = self.dtfr.loc[(self.dtfr.Stratum == h) & (self.dtfr.Domain == domain), var_y].sum()
					
				sum_a = self.dtfr.loc[(self.dtfr.Stratum == h), "Area"].sum()
				mean_hy = sum_y / sum_a
				
				sum_x = 0.0
				if self.dtfr[(self.dtfr.Stratum == h) & (self.dtfr.Domain == domain_p)].shape[0] > 0:
					sum_x = self.dtfr.loc[(self.dtfr.Stratum == h) & (self.dtfr.Domain == domain_p), var_x].sum()
					
				mean_hx = sum_x / sum_a
				l = (self.map_points[h] - 1) / (tot_points - 1) * self.covs[h] / float(self.dtfr.shape[0])
				c = (1 - self.weights[h]) *  self.covs[h] / float(self.dtfr.shape[0]) ** 2
				r = 1 / (tot_points - 1) * self.weights[h] * (mean_hy - mean_y) * (mean_hx - mean_x)
				tcov_h = l + c + r

			else:
				tcov_h = 0.0

			tcov += tcov_h
			
		tcov *= sum(self.areas.values()) ** 2
		
		return tcov
		
	
	def ratio_var(self, domain, domain_p, var_y, var_x, double_sampl = False, post_strat = False):
		cov = None
		var_y_dict = None 
		var_x_dict = None
		
		if double_sampl:
			if post_strat:
				cov = self.cov_double_post_stratified(domain, domain_p,  var_y, var_x)
				var_y_dict = self.double_post_stratified_mean_var(domain, var_y) 
				var_x_dict = self.double_post_stratified_mean_var(domain_p, var_x)
			else:
				cov = self.cov_double_stratified(domain, domain_p,  var_y, var_x)
				var_y_dict = self.double_stratified_mean_var(domain, var_y) 
				var_x_dict = self.double_stratified_mean_var(domain_p, var_x)
		else:
			if post_strat:
				cov = self.cov_post_stratified(domain, domain_p, var_y, var_x)
				var_y_dict = self.post_stratified_mean_var(domain, var_y) 
				var_x_dict = self.post_stratified_mean_var(domain_p, var_x)
			else:
				cov = self.cov_stratified(domain, domain_p,  var_y, var_x)
				var_y_dict = self.stratified_mean_var(domain, var_y) 
				var_x_dict = self.stratified_mean_var(domain_p, var_x)

		R = self.ratio(domain, domain_p, var_y, var_x)
		#print var_x_dict['Population total']
		
		var = (var_y_dict['Variance of the total'] +
				R ** 2 * var_x_dict['Variance of the total'] - 
				2 * R * cov) / var_x_dict['Population total'] ** 2
		
		stddev = var ** 0.5
		rel_error = stddev / R * 100

		# Confidence interval via Fieller's method
		Y = var_y_dict['Population total']
		X = var_x_dict['Population total']
		vY = var_y_dict['Variance of the total']
		vX = var_x_dict['Variance of the total']
		t_val = t.ppf(0.95, self.dtfr.shape[0] - 1)
		#print Y, X, vY, vX, t_val
		
		A = X * Y - t_val**2 * cov
		B = X**2 - t_val**2 * vX
		C = Y**2 - t_val**2 * vY
		#print A, B, C
		
		alpha0 = (A - (A**2 - B * C)**0.5) / B

		alpha1 = (A + (A**2 - B * C)**0.5) / B

		
		return {'Ratio': R,
			'Confidence interval': (alpha0, alpha1),
			'Variance of the ratio': var, 
			'Relative error': rel_error}
		
