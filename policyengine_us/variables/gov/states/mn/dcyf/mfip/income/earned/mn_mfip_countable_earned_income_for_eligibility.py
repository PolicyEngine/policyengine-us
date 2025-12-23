from policyengine_us.model_api import *


class mn_mfip_countable_earned_income_for_eligibility(Variable):
    value_type = float
    entity = SPMUnit
    label = "Minnesota MFIP countable earned income for eligibility"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/142G.16#stat.142G.16.1",
        "https://www.revisor.mn.gov/statutes/cite/256P.03#stat.256P.03.2",
    )
    defined_for = StateCode.MN

    def formula(spm_unit, period, parameters):
        # Per MN Stat. 142G.16, Subd. 1(b)(2):
        # For initial eligibility, dependent care costs must be deducted
        # from gross earned income before the $65 and 50% disregard.
        # Since dependent care is subtracted before 50%, its effect is halved.
        p = parameters(
            period
        ).gov.states.mn.dcyf.mfip.income.earned_income_disregard
        benefit_earned = spm_unit("mn_mfip_countable_earned_income", period)
        dependent_care = spm_unit("mn_mfip_dependent_care_deduction", period)
        # 50% disregard rate means dependent care effect is multiplied by 0.5
        dependent_care_adjustment = dependent_care * (1 - p.rate)
        return max_(benefit_earned - dependent_care_adjustment, 0)
