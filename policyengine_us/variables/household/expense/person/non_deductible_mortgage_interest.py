from policyengine_us.model_api import *


class non_deductible_mortgage_interest(Variable):
    value_type = float
    entity = Person
    label = "Non-deductible mortgage interest"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Home mortgage interest that is not deductible federally after "
        "applying the acquisition-debt caps."
    )

    def formula(person, period, parameters):
        non_deductible_interest = person.tax_unit(
            "non_deductible_mortgage_interest_tax_unit", period
        )
        share = person("home_mortgage_interest_share", period)
        return non_deductible_interest * share
