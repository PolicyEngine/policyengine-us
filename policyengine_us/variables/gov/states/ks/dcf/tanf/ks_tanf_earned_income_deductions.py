from policyengine_us.model_api import *


class ks_tanf_earned_income_deductions(Variable):
    value_type = float
    entity = SPMUnit
    label = "Kansas TANF earned income deductions"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://content.dcf.ks.gov/ees/keesm/implem_memo/2008_0326_TAF_ei_disregard.htm",
        "https://www.law.cornell.edu/regulations/kansas/K-A-R-30-4-110",
    )
    defined_for = StateCode.KS

    def formula(spm_unit, period, parameters):
        # Per KEESM Implementation Memo 2008-0326: 60% of earned income is
        # disregarded (only 40% counts toward benefit calculation)
        p = parameters(period).gov.states.ks.dcf.tanf.earned_income_disregard
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        return gross_earned * p.rate
