from policyengine_us.model_api import *


class ia_fip_net_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Iowa FIP net income eligible"
    definition_period = MONTH
    defined_for = StateCode.IA
    reference = "https://www.legis.iowa.gov/docs/iac/chapter/01-07-2026.441.41.pdf#page=20"

    def formula(spm_unit, period, parameters):
        # Test 2 for initial eligibility only
        # Net income = gross income - 20% earned income deduction
        # Must be < standard of need
        # Note: Does NOT include the 58% work incentive disregard
        p = parameters(period).gov.states.ia.dhs.fip.income
        gross_income = spm_unit("ia_fip_gross_income", period)
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        earned_income_deduction = gross_earned * p.earned_income_deduction
        net_income = gross_income - earned_income_deduction
        standard_of_need = spm_unit("ia_fip_standard_of_need", period)
        return net_income < standard_of_need
