from policyengine_us.model_api import *


class home_sale_taxable_gain(Variable):
    value_type = float
    entity = Person
    label = "Taxable long-term gain on the sale of a main home"
    documentation = "Gain above the section 121 exclusion, long-term when the home was owned more than 12 months."
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/121"

    def formula(person, period, parameters):
        taxable = max_(
            0,
            person("home_sale_gain", period)
            - person("home_sale_gain_exclusion", period),
        )
        return where(person("home_sale_ownership_months", period) > 12, taxable, 0)
