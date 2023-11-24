from policyengine_us.model_api import *


class mt_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana additions to federal AGI"
    unit = USD
    definition_period = YEAR
    reference = "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/05/Montana-Idividiual-Income-Tax-Return-Form-2-2022v6.2.pdf#page=4",
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        additions = tax_unit("mt_other_additions", period)
        mt_social_security_benefit = tax_unit(
            "mt_social_security_benefits", period
        )
        taxable_social_security = tax_unit(
            "tax_unit_taxable_social_security", period
        )
        # The ss benefits act as additions of the benefit is larger than the taxable portion
        # of social security, otherwise it is a subtarction
        reduced_ss_benefit = max_(
            mt_social_security_benefit - taxable_social_security, 0
        )
        return additions + reduced_ss_benefit
