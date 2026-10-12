from policyengine_us.model_api import *


class ne_child_care_subsidy_family_fee(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = MONTH
    label = "Nebraska Child Care Subsidy monthly family fee"
    defined_for = StateCode.NE
    reference = (
        "https://dhhs.ne.gov/Guidance%20Docs/Title%20392%20-%20Child%20Care%20Subsidy.pdf#page=4",
        "https://dhhs.ne.gov/Child%20Care%20Documents/ACF-118%20CCDF%20FFY%202025-2027%20For%20Nebraska%20-%20APPROVED.pdf#page=39",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ne.dhhs.child_care_subsidy
        gross_income = spm_unit("ne_child_care_subsidy_gross_income", period)
        fpg = spm_unit("ne_child_care_subsidy_fpg", period)
        fee_free_limit = np.ceil(fpg * p.fpg_fraction.fee_free_limit)
        fee_free = gross_income <= fee_free_limit
        waived = spm_unit("is_tanf_enrolled", period) | spm_unit(
            "ne_child_care_subsidy_categorical_waived", period
        )
        return where(fee_free | waived, 0, max_(gross_income, 0) * p.rate)
