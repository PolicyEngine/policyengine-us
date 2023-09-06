from policyengine_us.model_api import *


class wv_social_security_benefits_subtraction_eligible(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia social security deduction eligible"
    unit = USD
    definition_period = YEAR
    reference = "https://tax.wv.gov/Documents/PIT/2022/PersonalIncomeTaxFormsAndInstructions.2022.pdf#page=25"
    defined_for = StateCode.WV

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        agi = tax_unit("adjusted_gross_income", period)
        p = parameters(
            period
        ).gov.states.wv.tax.income.subtractions.social_security_benefits
        return agi <= p.threshold[filing_status]