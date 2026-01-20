from policyengine_us.model_api import *


class ia_fip_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Iowa FIP income eligible"
    definition_period = YEAR
    defined_for = StateCode.IA
    reference = (
        "https://www.legis.iowa.gov/docs/iac/chapter/01-07-2026.441.41.pdf"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ia.dhs.fip.income
        # three step income test
        # test 1: countable gross income below some percentage of standard of need
        gross_income = spm_unit("ia_fip_gross_income", period)
        standard_of_need = spm_unit("ia_fip_standard_of_need", period)
        gross_income_limit = standard_of_need * p.gross_income_limit_percent
        gross_income_eligible = gross_income <= gross_income_limit

        # test 2: countable net income below standard of need
        gross_earned_income = spm_unit("ia_fip_gross_earned_income", period)
        earned_income_deduction = (
            gross_earned_income * p.earned_income_deduction
        )
        net_income = gross_income - earned_income_deduction
        net_income_eligible = net_income < standard_of_need

        # test 3: countable net income below payment standard
        countable_income = spm_unit("ia_fip_countable_income", period)
        payment_standard = spm_unit("ia_fip_payment_standard", period)
        payment_standard_eligible = countable_income < payment_standard

        return (
            gross_income_eligible
            & net_income_eligible
            & payment_standard_eligible
        )
