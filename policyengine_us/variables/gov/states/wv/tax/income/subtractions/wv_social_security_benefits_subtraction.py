from policyengine_us.model_api import *


class wv_social_security_benefits_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia social security deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://tax.wv.gov/Documents/PIT/2022/PersonalIncomeTaxFormsAndInstructions.2022.pdf#Page=25"
    defined_for = "wv_social_security_benefits_subtraction_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.wv.tax.income.subtractions.social_security_benefits
        person = tax_unit.members
        amount = person(
            "social_security", period # or use taxable_social_security?
        ) * p.rate
        return tax_unit.sum(amount)
