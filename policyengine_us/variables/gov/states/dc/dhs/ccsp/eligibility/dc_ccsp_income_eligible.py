from policyengine_us.model_api import *


class dc_ccsp_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for DC Child Care Subsidy Program (CCSP) due to income"
    definition_period = MONTH
    reference = "https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/DC%20Child%20Care%20Subsidy%20Program%20Policy%20Manual.pdf#page=12"
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.dc.dhs.ccsp.income.income_limit
        countable_income = spm_unit("dc_ccsp_countable_income", period)
        fpg = spm_unit("spm_unit_fpg", period)
        smi = spm_unit("hhs_smi", period)
        enrolled_in_ccsp = spm_unit("dc_ccsp_enrolled", period)
        new_applicants_income_limit = fpg * p.new_applicants_rate
        redetermination_income_limit = smi * p.redetermination_rate
        income_limit = where(
            enrolled_in_ccsp,
            redetermination_income_limit,
            new_applicants_income_limit,
        )
        return countable_income <= income_limit
