from policyengine_us.model_api import *


class la_ccap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Louisiana CCAP income eligible"
    reference = "https://www.doa.la.gov/media/043btqeh/28v165.docx"
    defined_for = StateCode.LA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.la.ldoe.ccap
        income = spm_unit("la_ccap_countable_income", period)
        monthly_smi = spm_unit("la_ccap_smi", period)
        # LAC 28:CLXV.509.A.3: countable income at or below 85% of the
        # state median income.
        return income <= p.income.limit * monthly_smi
