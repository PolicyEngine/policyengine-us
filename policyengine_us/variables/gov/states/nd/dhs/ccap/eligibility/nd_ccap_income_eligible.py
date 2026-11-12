from policyengine_us.model_api import *


class nd_ccap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "North Dakota CCAP income eligible"
    definition_period = MONTH
    defined_for = StateCode.ND
    reference = (
        "https://www.nd.gov/dhs/policymanuals/40028/Content/400_28_25_15.htm",
        "https://www.nd.gov/dhs/policymanuals/40028/Content/400_28_20_40.htm",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nd.dhs.ccap.income
        countable_income = spm_unit("nd_ccap_countable_income", period)
        enrolled = spm_unit("is_nd_ccap_enrolled", period)
        # Initial applicants are tested against 75% of the state median income;
        # enrolled recipients are tested against 85% under the graduated
        # eligibility rule (400-28-25-15). hhs_smi is an annual dollar amount,
        # so reading it with the bare monthly period auto-divides it to a
        # monthly value.
        monthly_smi = spm_unit("hhs_smi", period)
        initial_limit = monthly_smi * p.initial_smi_rate
        continuing_limit = monthly_smi * p.continuing_smi_rate
        income_limit = where(enrolled, continuing_limit, initial_limit)
        # North Dakota excludes all income while a caretaker qualifies for the
        # Workforce Benefit, including at review (400-28-20-40). After that
        # qualification ends, enrolled families face the ordinary 85% limit.
        workforce = spm_unit("nd_ccap_workforce_benefit_eligible", period)
        return (countable_income <= income_limit) | workforce
