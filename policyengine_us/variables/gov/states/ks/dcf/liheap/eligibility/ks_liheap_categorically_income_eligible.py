from policyengine_us.model_api import *


class ks_liheap_categorically_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Kansas LIEAP categorically income eligible"
    documentation = "Households with a member receiving TANF, SSI or SNAP are considered income eligible for Kansas LIEAP heating assistance."
    reference = "https://liheapch.acf.gov/docs/2026/state-plans/KS_Plan_2026.pdf#page=5"
    defined_for = StateCode.KS

    def formula(spm_unit, period, parameters):
        receives_ssi = add(spm_unit, period, ["ssi"]) > 0
        receives_snap = spm_unit("snap", period) > 0
        receives_tanf = spm_unit("ks_tanf", period) > 0
        return receives_ssi | receives_snap | receives_tanf
