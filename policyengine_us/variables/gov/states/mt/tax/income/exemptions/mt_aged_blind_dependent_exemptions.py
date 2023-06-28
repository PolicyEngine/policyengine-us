from policyengine_us.model_api import *


class mt_aged_blind_dependent_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana aged blind dependent exemptions"
    unit = USD
    definition_period = YEAR
    reference = "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/05/Montana-Idividiual-Income-Tax-Return-Form-2-2022v6.2.pdf"
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        base_exemption = tax_unit("mt_base_exemption", period)
        aged_exemption = tax_unit("mt_aged_exemption", period)
        blind_exemption = tax_unit("mt_blind_exemption", period)
        dependent_exemption = tax_unit("mt_dependent_exemption", period)
        return (
            base_exemption
            + aged_exemption
            + blind_exemption
            + dependent_exemption
        )
