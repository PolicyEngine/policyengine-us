from policyengine_us.model_api import *


class sc_tanf_countable_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "South Carolina TANF countable income eligible"
    definition_period = MONTH
    defined_for = StateCode.SC
    reference = "https://dss.sc.gov/media/ojqddxsk/tanf-policy-manual-volume-65.pdf#page=131"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.sc.tanf.income
        fpg = spm_unit("tanf_fpg", period)
        need_standard = fpg * p.need_standard.rate
        countable_income = spm_unit("sc_tanf_countable_income", period)
        return countable_income < need_standard
