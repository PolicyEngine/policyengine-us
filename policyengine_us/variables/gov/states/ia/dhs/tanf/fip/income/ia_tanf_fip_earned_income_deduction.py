from policyengine_us.model_api import *


class ia_tanf_fip_earned_income_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Iowa FIP 20% earned income deduction"
    unit = USD
    definition_period = MONTH
    reference = "Iowa Administrative Code 441-41.27"
    documentation = "https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-27"
    defined_for = StateCode.IA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ia.dhs.tanf.fip
        gross_earned = spm_unit("ia_tanf_fip_gross_earned_income", period)

        return gross_earned * p.deductions.earned_income_deduction_rate
