from policyengine_us.model_api import *


class required_minimum_distribution_employer_plan(Variable):
    value_type = float
    entity = Person
    label = "Required minimum distribution from the person's own employer plans"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/401#a_9_C",
        "https://www.law.cornell.edu/cfr/text/26/1.401(a)(9)-5",
    )

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.irs.retirement_distributions.required_minimum_distributions
        qlac_ok = person("rmd_qlac_premiums_paid", period) <= p.qlac_premium_limit
        balance = max_(
            0,
            person("rmd_employer_plan_prior_year_end_balance", period)
            - qlac_ok * max_(0, person("rmd_qlac_value_employer_plan", period)),
        )
        distribution_period = person("rmd_distribution_period", period)
        amount = np.divide(
            balance,
            distribution_period,
            out=np.zeros_like(balance),
            where=distribution_period > 0,
        )
        return where(person("rmd_employer_plan_still_working", period), 0, amount)
