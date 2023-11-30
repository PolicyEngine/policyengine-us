from policyengine_us.model_api import *


class mt_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana subtractions from federal AGI"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://rules.mt.gov/gateway/Subchapterhome.asp?scn=42%2E15%2E2",
        "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/05/Montana-Idividiual-Income-Tax-Return-Form-2-2022v6.2.pdf#page=5",
    )
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        subtractions = tax_unit("mt_other_subtractions", period)
        mt_social_security_benefit = tax_unit(
            "mt_social_security_benefits", period
        )
        taxable_social_security = tax_unit(
            "tax_unit_taxable_social_security", period
        )
        # The ss benefits act as subtractions of the benefit is smaller than the taxable portion
        # of social security, otherwise it is a addition
        exceeded_ss_benefit = max_(
            taxable_social_security - mt_social_security_benefit, 0
        )
        return subtractions + exceeded_ss_benefit
