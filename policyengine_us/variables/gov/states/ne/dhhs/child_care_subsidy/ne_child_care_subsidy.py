from policyengine_us.model_api import *


class ne_child_care_subsidy(Variable):
    value_type = float
    unit = USD
    entity = SPMUnit
    label = "Nebraska Child Care Subsidy"
    definition_period = MONTH
    reference = (
        "https://dhhs.ne.gov/Documents/CC-Subsidy-Provider-Booklet.pdf#page=28",
        "https://dhhs.ne.gov/Child%20Care%20Documents/ACF-118%20CCDF%20FFY%202025-2027%20For%20Nebraska%20-%20APPROVED.pdf#page=52",
    )
    defined_for = "ne_child_care_subsidy_eligible"

    def formula(spm_unit, period, parameters):
        state_maximum = add(
            spm_unit,
            period,
            [
                "ne_child_care_subsidy_maximum_provider_rate",
                "ne_child_care_subsidy_optional_fees",
            ],
        )
        private_charge = spm_unit("spm_unit_pre_subsidy_childcare_expenses", period)
        reimbursement = min_(state_maximum, private_charge)
        family_fee = spm_unit("ne_child_care_subsidy_family_fee", period)
        return max_(reimbursement - family_fee, 0)
