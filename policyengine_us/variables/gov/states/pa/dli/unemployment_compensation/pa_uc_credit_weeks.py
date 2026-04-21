from policyengine_us.model_api import *


class pa_uc_credit_weeks(Variable):
    value_type = int
    entity = Person
    label = "Pennsylvania unemployment compensation credit weeks"
    unit = "week"
    definition_period = YEAR
    reference = (
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dli/documents/uc/uc_law.pdf#page=16",
    )
    defined_for = StateCode.PA
