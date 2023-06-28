from policyengine_us.model_api import *


class mt_blind_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana blind exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/05/Montana-Idividiual-Income-Tax-Return-Form-2-2022v6.2.pdf"
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.exemptions
        # Count number of is_blind from tax_unit
        blind_head = tax_unit("blind_head", period).astype(int)
        blind_spouse = tax_unit("blind_spouse", period) * 1
        return (blind_head + blind_spouse) * p.amount
