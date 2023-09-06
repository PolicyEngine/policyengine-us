from policyengine_us.model_api import *


class wv_social_security_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia social security deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://tax.wv.gov/Documents/PIT/2022/PersonalIncomeTaxFormsAndInstructions.2022.pdf#Page=25"
    defined_for = "wv_social_security_deduction_eligible"

    def formula(tax_unit, period):
        return tax_unit(
            "wv_social_security_benefit", period
        )
