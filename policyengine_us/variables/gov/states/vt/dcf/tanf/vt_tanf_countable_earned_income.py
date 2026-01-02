from policyengine_us.model_api import *


class vt_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Vermont TANF countable earned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://law.justia.com/codes/vermont/title-33/chapter-11/section-1103/",
        "https://www.law.cornell.edu/regulations/vermont/13-220-Code-Vt-R-13-170-220-X",
    )
    defined_for = StateCode.VT

    def formula(spm_unit, period, parameters):
        # Per 33 V.S.A. Section 1103(a)(3): First $350 and 25% of remainder disregarded
        p = parameters(period).gov.states.vt.dcf.tanf.income.disregard.earned
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        # Countable = (Gross - flat_disregard) × (1 - rate)
        after_flat = max_(gross_earned - p.flat, 0)
        return after_flat * (1 - p.rate)
