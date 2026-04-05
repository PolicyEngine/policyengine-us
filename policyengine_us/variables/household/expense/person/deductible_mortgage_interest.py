from policyengine_us.model_api import *


class deductible_mortgage_interest(Variable):
    value_type = float
    entity = Person
    label = "Deductible mortgage interest"
    documentation = (
        "Federal deductible mortgage interest. When structural mortgage inputs "
        "are provided at the tax-unit level, PolicyEngine applies the "
        "acquisition-debt caps and allocates the resulting deduction across "
        "filers."
    )
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/163"

    def formula(person, period, parameters):
        deductible_interest = person.tax_unit(
            "deductible_mortgage_interest_tax_unit", period
        )
        share = person("home_mortgage_interest_share", period)
        return deductible_interest * share
