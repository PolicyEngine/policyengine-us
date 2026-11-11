from policyengine_us.model_api import *


class household_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Child care subsidies counted in household benefits"
    documentation = (
        "Child care subsidies up to the family's pre-subsidy bill for child "
        "care and after-school care. A payment above a provider's bill goes "
        "to that provider, not the family, and pays none of another "
        "provider's bill. With no bill recorded, the whole subsidy counts."
    )
    unit = USD
    reference = (
        # PDF pages 1-2
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/CDD/CCFAP/CCFAP-Understanding-Payments.pdf#page=1",
        # PDF pages 1, 7 and 10
        "https://outside.vermont.gov/dept/DCF/Policies%20Procedures%20Guidance/CDD-Memo-UPK-and-CCFAP-family-tuition-Summer-2026-Update.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        subsidies = spm_unit("child_care_subsidies", period)
        above_bills = spm_unit("child_care_subsidies_above_provider_bills", period)
        # Colorado's subsidy pays for after-school care too (co_ccap_subsidy).
        bill = add(
            spm_unit,
            period,
            ["pre_subsidy_childcare_expenses", "after_school_expenses"],
        )
        return where(bill > 0, min_(subsidies - above_bills, bill), subsidies)
