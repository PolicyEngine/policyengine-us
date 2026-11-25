from policyengine_us.model_api import *


class early_distribution_simple_ira_tax_base(Variable):
    value_type = float
    entity = Person
    label = "Early SIMPLE IRA distributions subject to the two-year additional tax rate"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/72#t_6"

    def formula(person, period, parameters):
        return max_(
            0,
            person("early_distributions_from_simple_ira_first_two_years", period)
            - max_(person("early_distribution_exceptions_simple_ira", period), 0),
        )
