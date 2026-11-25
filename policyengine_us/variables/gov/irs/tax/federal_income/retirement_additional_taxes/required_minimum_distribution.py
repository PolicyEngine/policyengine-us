from policyengine_us.model_api import *


class required_minimum_distribution(Variable):
    value_type = float
    entity = Person
    label = "Required minimum distribution due this year"
    documentation = "Owner required distributions from IRAs and employer plans due by the end of the year, plus a deferred first-year amount and inherited-account amounts."
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/401#a_9",
        "https://www.law.cornell.edu/cfr/text/26/1.401(a)(9)-5",
        "https://www.irs.gov/publications/p590b",
    )

    def formula(person, period, parameters):
        return (
            person("required_minimum_distribution_ira", period)
            + person("required_minimum_distribution_employer_plan", period)
            + max_(0, person("rmd_prior_year_deferred_amount", period))
            + max_(0, person("rmd_inherited_required_amount", period))
        )
