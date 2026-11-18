from policyengine_us.model_api import *


class household_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Child care subsidies counted in household benefits"
    documentation = (
        "Child care subsidies up to the family's pre-subsidy bill for child "
        "care and after-school care. A payment above the bill goes to the "
        "provider, not the family. With no bill recorded, the whole subsidy "
        "counts."
    )
    unit = USD
    reference = (
        # PDF pages 1-2
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/CDD/CCFAP/CCFAP-Understanding-Payments.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        subsidies = spm_unit("child_care_subsidies", period)
        # Colorado's subsidy pays for after-school care too (co_ccap_subsidy).
        bill = add(
            spm_unit,
            period,
            ["pre_subsidy_childcare_expenses", "after_school_expenses"],
        )
        return where(bill > 0, min_(subsidies, bill), subsidies)
