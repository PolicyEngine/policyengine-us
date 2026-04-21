from policyengine_us.model_api import *


class pa_uc_gross_weekly_earnings(Variable):
    value_type = float
    entity = Person
    label = "Pennsylvania unemployment compensation gross weekly earnings"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dli/documents/uc/uc_law.pdf#page=133",
    )
    defined_for = StateCode.PA
