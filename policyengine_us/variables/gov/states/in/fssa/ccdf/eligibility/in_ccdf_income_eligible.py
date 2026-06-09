from policyengine_us.model_api import *


class in_ccdf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Indiana CCDF income eligible"
    definition_period = MONTH
    defined_for = StateCode.IN
    reference = "https://www.in.gov/fssa/carefinder/files/CCDF-Policy-Manual.pdf#page=5"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states["in"].fssa.ccdf.income
        countable_income = spm_unit("in_ccdf_countable_income", period)
        enrolled = spm_unit("is_in_ccdf_enrolled", period)
        # Initial applicants are tested at 135% of the federal poverty guideline;
        # enrolled recipients are tested at 85% of the state median income.
        initial_limit = spm_unit("spm_unit_fpg", period) * p.get_on_fpg_rate
        continuing_limit = spm_unit("hhs_smi", period) * p.stay_on_smi_rate
        income_limit = where(enrolled, continuing_limit, initial_limit)
        return countable_income <= income_limit
