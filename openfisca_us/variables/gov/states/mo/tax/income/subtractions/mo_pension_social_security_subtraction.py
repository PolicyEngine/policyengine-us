from openfisca_us.model_api import *


class mo_pension_social_security_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = " MO Pensions and Social Security/Social Security Disability Payments Subtractions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/forms/MO-A_2021.pdf#page=3",
        "https://revisor.mo.gov/main/OneSection.aspx?section=143.124",
    )

    def formula(tax_unit, period, parameters):
        mo_agi = tax_unit("mo_adjusted_gross_income", period)
        #public pension calculation
        taxable_social_security = tax_unit("tax_unit_taxable_social_security", period)
        agi_less_ss = mo_agi - taxable_social_security
        p = parameters(period).gov.states.mo.tax.income.subtractions.mo_pension_and_social_security_subtraction
        
        public_pension_exemption_threshold = p.social_security_exemption_thresholds
        amount_past_exemption = agi_less_ss - public_pension_exemption_threshold

        

