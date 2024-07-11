from policyengine_us.model_api import *


class va_total_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia exemptions"
    defined_for = StateCode.VA
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"
    )
    adds = ["va_personal_exemption", "va_aged_blind_exemption"]
