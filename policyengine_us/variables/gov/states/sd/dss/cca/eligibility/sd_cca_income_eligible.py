from policyengine_us.model_api import *


class sd_cca_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "South Dakota CCA income eligible"
    definition_period = MONTH
    defined_for = StateCode.SD
    reference = "https://dss.sd.gov/docs/childcare/assistance/Subsidy_Manual.pdf#page=8"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.sd.dss.cca.income
        countable_income = spm_unit("sd_cca_countable_income", period)
        enrolled = spm_unit("is_sd_cca_enrolled", period)
        # spm_unit_fpg and hhs_smi are annual dollar amounts, so reading them
        # with the bare monthly period auto-divides them to monthly values.
        monthly_fpg = spm_unit("spm_unit_fpg", period)
        monthly_smi = spm_unit("hhs_smi", period)
        smi_limit = monthly_smi * p.smi_limit
        # Initial applicants must be at or below the lesser of 209% of the
        # federal poverty level and 85% of the state median income. Continuing
        # recipients remain eligible up to 85% of the state median income under
        # the graduated phase-out.
        initial_limit = min_(monthly_fpg * p.fpl_limit, smi_limit)
        income_limit = where(enrolled, smi_limit, initial_limit)
        return countable_income <= income_limit
