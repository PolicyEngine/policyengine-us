from policyengine_us.model_api import *


class va_personal_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia personal exemption"
    defined_for = StateCode.VA
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"
    )

    adds = ["va_personal_exemption_person"]
