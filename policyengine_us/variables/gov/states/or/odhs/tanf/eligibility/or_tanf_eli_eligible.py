from policyengine_us.model_api import *


class or_tanf_eli_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Oregon TANF eligible for Exit Limit Increase (ELI) standards"
    definition_period = MONTH
    reference = "https://oregon.public.law/rules/oar_461-155-0030"
    defined_for = StateCode.OR

    def formula(spm_unit, period, parameters):
        # ELI applies when currently enrolled in TANF AND has earned income
        is_enrolled = spm_unit("is_tanf_enrolled", period)
        earned_income = add(spm_unit, period, ["tanf_gross_earned_income"])
        return is_enrolled & (earned_income > 0)
