from policyengine_us.model_api import *


class medicare_gross_cost(Variable):
    value_type = float
    entity = Person
    label = "Gross Medicare cost"
    documentation = (
        "Annual Medicare spending on behalf of the beneficiary before "
        "subtracting beneficiary premiums. This matches the gross Medicare "
        "benefit concept used in the CBO household-income framework."
    )
    unit = USD
    definition_period = YEAR
    reference = "https://www.cms.gov/medicare"
    defined_for = "medicare_enrolled"

    def formula(person, period, parameters):
        return parameters(period).calibration.gov.hhs.medicare.per_capita_cost
