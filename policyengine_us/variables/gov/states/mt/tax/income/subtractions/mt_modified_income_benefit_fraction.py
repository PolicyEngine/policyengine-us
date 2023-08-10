from policyengine_us.model_api import *

class mt_modified_income_benefit_fraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana modified AGI benefits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/05/Montana-Idividiual-Income-Tax-Return-Form-2-2022v6.2.pdf"
        ""
    )
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.subtractions
        total_benefit_fraction = p.social_security.total_benefit_fraction1
        #Line1
        net_benefits = tax_unit.spm_unit("spm_unit_benefits", period)
        return net_benefits * total_benefit_fraction
