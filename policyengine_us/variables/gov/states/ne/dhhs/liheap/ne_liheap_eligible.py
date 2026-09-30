from policyengine_us.model_api import *


class ne_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Nebraska LIHEAP regular heating assistance eligibility"
    defined_for = StateCode.NE
    reference = (
        "https://rules.nebraska.gov/rules?agencyId=37&titleId=231",
        "https://dhhs.ne.gov/Documents/LIHEAP%20State%20Plan.pdf#page=9",
    )

    def formula(spm_unit, period, parameters):
        income_eligible = spm_unit("ne_liheap_income_eligible", period)
        # 476 NAC 1-004.09 includes energy paid through rent; FY2026 plan 2.3
        # allows such renters when responsible for a portion of heating costs.
        # Economic vulnerability still requires exposure to energy-cost increases
        # (1-004.06 and 2-002(A)); the heat-in-rent flag cannot establish this.
        # The positive-bill proxy below misses eligible renters without a separate
        # bill. This is a coverage gap, not a legal exclusion of heat-in-rent
        # households. Administrative disqualifications also remain unmodeled.
        responsible = spm_unit("heating_expense", period) > 0
        return income_eligible & responsible
