from policyengine_us.model_api import *


class ok_tanf_eid_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Oklahoma TANF earned income disregard"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/oklahoma/OAC-340-10-3-31.1"
    )
    defined_for = StateCode.OK

    def formula(spm_unit, period, parameters):
        # Per OAC 340:10-3-31.1(a): EID applies when gross earned income <= $2,064
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        p = parameters(period).gov.states.ok.dhs.tanf.income
        return gross_earned <= p.disregard.cap
