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
    )

    def formula(spm_unit, period, parameters):
        countable_income = spm_unit("wa_wccc_countable_income", period)
        income_limit = spm_unit("wa_wccc_smi_limit", period)
        # RCW 43.216.802(5) also extends income eligibility to households
        # receiving SNAP, but WA's 60-65% SMI limit already exceeds SNAP's
        # 130% FPL gross income test for typical household sizes, so the
        # SNAP categorical branch is not modeled at the moment.
        return countable_income <= income_limit
