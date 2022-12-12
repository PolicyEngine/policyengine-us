from policyengine_us.model_api import *


class md_two_income_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD two-income married couple subtraction from AGI"
    unit = USD
    definition_period = YEAR
    reference = "https://www.marylandtaxes.gov/forms/21_forms/Resident_Booklet.pdf#page=16"
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        pass
