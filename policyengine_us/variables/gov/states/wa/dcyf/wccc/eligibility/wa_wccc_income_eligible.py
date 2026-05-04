from policyengine_us.model_api import *


class wa_wccc_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Income eligible for Washington WCCC"
    definition_period = MONTH
    defined_for = StateCode.WA
    reference = (
        "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0005",
        "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0023",
        "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0075",
        "https://app.leg.wa.gov/RCW/default.aspx?cite=43.216.802",
    )

    def formula(spm_unit, period, parameters):
        countable_income = spm_unit("wa_wccc_countable_income", period)
        income_limit = spm_unit("wa_wccc_smi_limit", period)
        under_smi_limit = countable_income <= income_limit
        # RCW 43.216.802(5): when an applicant or consumer is a member of an
        # assistance unit that is "eligible for or receiving" basic food
        # benefits under SNAP or the State Food Assistance Program, the
        # department must determine that the income eligibility requirements
        # are met. SFAP is not modeled at the moment.
        snap_categorical = spm_unit("is_snap_eligible", period) | (
            spm_unit("snap_reported", period) > 0
        )
        return under_smi_limit | snap_categorical
