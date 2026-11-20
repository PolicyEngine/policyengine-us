from policyengine_us.model_api import *


class assigned_ct_temporary_premium_assistance(Variable):
    value_type = float
    entity = TaxUnit
    label = "Assigned Connecticut Temporary Premium Assistance"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CT
    reference = (
        "https://www.accesshealthct.com/article/active/new-financial-help-could-lower-your-health-coverage-costs-in-2026/",
    )
    documentation = (
        "Temporary Premium Assistance for a tax unit that takes up "
        "Marketplace coverage. Access Health CT sends the payment to the "
        "insurer each month, so only enrollees receive it; this mirrors "
        "assigned_aca_ptc and uses the same take-up draw "
        "(takes_up_aca_if_eligible). Take-up is assigned at microdata "
        "construction, so at the default take-up flag this equals the "
        "amount."
    )

    def formula(tax_unit, period, parameters):
        return tax_unit("ct_temporary_premium_assistance", period) * tax_unit(
            "takes_up_aca_if_eligible", period
        )
