from policyengine_us.model_api import *


class ma_tafdc_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) due to income"
    definition_period = YEAR
    reference = "https://www.mass.gov/how-to/transitional-aid-to-families-with-dependent-children-tafdc"
    defined_for = StateCode.MA

    def formula(spm_unit, period, parameters):
        income = spm_unit("ma_tafdc_gross_income", period)
        income_limit = spm_unit("ma_tafdc_income_limit", period)
        return income < income_limit
 