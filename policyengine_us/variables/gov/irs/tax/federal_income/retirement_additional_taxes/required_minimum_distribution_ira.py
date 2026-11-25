from policyengine_us.model_api import *


class required_minimum_distribution_ira(Variable):
    value_type = float
    entity = Person
    label = "Required minimum distribution from the person's own IRAs"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/408#a_6",
        "https://www.law.cornell.edu/cfr/text/26/1.408-8",
        "https://www.irs.gov/publications/p590b",
    )

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.irs.retirement_distributions.required_minimum_distributions
        qlac_ok = person("rmd_qlac_premiums_paid", period) <= p.qlac_premium_limit
        balance = max_(
            0,
            person("rmd_ira_prior_year_end_balance", period)
            - qlac_ok * max_(0, person("rmd_qlac_value_ira", period)),
        )
        distribution_period = person("rmd_distribution_period", period)
        return np.divide(
            balance,
            distribution_period,
            out=np.zeros_like(balance),
            where=distribution_period > 0,
        )
