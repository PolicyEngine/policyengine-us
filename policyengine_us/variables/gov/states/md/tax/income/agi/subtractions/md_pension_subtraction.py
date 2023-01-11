from policyengine_us.model_api import *


class md_pension_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD pension subtraction from AGI"
    unit = USD
    definition_period = YEAR
    reference = "https://www.marylandtaxes.gov/forms/21_forms/Resident_Booklet.pdf#page=13"
    defined_for = StateCode.MD

    adds = ["md_pension_subtraction_amount"]
