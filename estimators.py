from pandas import DataFrame
from scipy.stats import t

class Estimator(object):
	
	def __init__(self, dtfr, areas, weights):
		
		if isinstance(dtfr, DataFrame):
			self.dtfr = dtfr
		
		self.strata_areas = areas
		self.weights = weights
		self.s2 = None # Strata variances
		self.map_points = None
		self.covs = None
		

	def domain_mean(self, domain, variable):
		tot = 0.0
		
		for h in self.strata_areas:
		
			if self.dtfr[(self.dtfr.Stratum == h) & (self.dtfr.Domain == domain)].shape[0] > 0:
		
				sum_y = self.dtfr.loc[(self.dtfr.Stratum == h) & (self.dtfr.Domain == domain), variable].sum()
				sum_a = float(self.dtfr.loc[(self.dtfr.Stratum == h), "Area"].sum())
				str_mean = sum_y / sum_a
				tot += str_mean * self.strata_areas[h]
		
		tot /= sum(self.strata_areas.values())
		
		return tot
		
	def var_total(self, var_dict):
		return sum(self.strata_areas.values()) ** 2 * sum(var_dict.values())


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
		poptot = sum(self.strata_areas.values()) * mean
		conf_inter = t.interval(confidence, self.dtfr.shape[0] - 1, poptot, std_err) 
		out = {'Domain mean': mean,
			'Population total': poptot,
			'Strata variances': sv, 
			'Variance of the total': vartot, 
			'Confidence interval': conf_inter}
		
		return out
		
	def post_stratified_mean_var(self, domain, variable):
		pv = {}
		self.get_strata_var(domain, variable)
		
		for h in self.s2:
			pv[h] = self.weights[h] * self.s2[h] 
			pv[h] += ((1 - self.weights[h]) * self.s2[h]) / self.dtfr.shape[0]
			pv[h] /= self.dtfr.shape[0]

		return pv


	def double_stratified_mean_var(self, domain,  variable):
		
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
		
		return sv	
		

	def double_post_stratified_mean_var(self, domain,  variable):
		
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
		
		return sv
	

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
			
		tcov *= sum(self.strata_areas.values()) ** 2
		
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
		tcov *= sum(self.strata_areas.values()) ** 2
		
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
			
		tcov *= sum(self.strata_areas.values()) ** 2
		
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
			
		tcov *= sum(self.strata_areas.values()) ** 2
		
		return tcov
