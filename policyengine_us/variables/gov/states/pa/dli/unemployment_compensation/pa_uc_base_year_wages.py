from policyengine_us.model_api import *


class pa_uc_base_year_wages(Variable):
    value_type = float
    entity = Person
    label = "Pennsylvania unemployment compensation base year wages"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dli/documents/uc/uc_law.pdf#page=119",
    )
    defined_for = StateCode.PA
