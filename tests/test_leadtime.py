import unittest
from research_lab.leadtime import (pinball, newsvendor_cost, lag_variance, gaussian_expected_cost, evaluate_cell, run_protocol)

C={'question_id':'leadtime-quantile','generator_version':'gaussian-ar1-v1','mean':100.,'sigma':10.,'phase':'confirmatory','frozen':True,'trials_per_seed':20,'seeds':[101,103,107], 'lead_times':[1,3],'rhos':[0.,0.6], 'alphas':[.9], 'paddings':[.45]}

class LeadtimeTests(unittest.TestCase):
    def test_proper_score_exact_identity(self):
        for y,q in [(1.,2.),(3.,2.),(2.,2.)]:
            self.assertAlmostEqual(newsvendor_cost(y,q,.9),pinball(y,q,.9))
    def test_variance_independence_and_correlation(self):
        self.assertEqual(lag_variance(7,0.),7)
        self.assertGreater(lag_variance(7,.6),7)
        self.assertEqual(lag_variance(1,.6),1)
    def test_analytic_oracle_optimum(self):
        mean,sd,alpha=700.,30.,.9
        from statistics import NormalDist
        q=mean+NormalDist().inv_cdf(alpha)*sd
        baseline=gaussian_expected_cost(mean,sd,q,alpha)
        self.assertLess(baseline,gaussian_expected_cost(mean,sd,q-10,alpha))
        self.assertLess(baseline,gaussian_expected_cost(mean,sd,q+10,alpha))
    def test_reproducibility_and_confirmation_freeze(self):
        self.assertEqual(evaluate_cell(C,7,.6,.9,.45,101),evaluate_cell(C,7,.6,.9,.45,101))
        self.assertEqual(run_protocol(C),run_protocol(C))
        with self.assertRaises(ValueError):run_protocol({**C,'frozen':False})
    def test_negative_control_and_true_oracle(self):
        from statistics import NormalDist
        alpha=.9
        mu=100.;sigma=10.;length=7
        qa=length*mu+NormalDist().inv_cdf(alpha)*sigma*(length**.5)
        qb=length*mu+NormalDist().inv_cdf(alpha)*sigma*(length**.5)*1.45
        independent=gaussian_expected_cost(length*mu,sigma*(length**.5),qa,alpha)
        worse=gaussian_expected_cost(length*mu,sigma*(length**.5),qb,alpha)
        self.assertLess(independent,worse)

if __name__=='__main__':unittest.main()
