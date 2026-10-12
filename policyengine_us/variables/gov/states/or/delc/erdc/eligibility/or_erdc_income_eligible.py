from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class or_erdc_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Eligible for Oregon ERDC based on income"
    defined_for = StateCode.OR
    reference = (
        "https://secure.sos.state.or.us/oard/view.action?ruleNumber=414-175-0050"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states["or"].delc.erdc
        expanded_child_welfare = spm_unit(
            "or_erdc_expanded_child_welfare_eligible", period
        )
        countable_income = spm_unit("or_erdc_countable_income", period)
        size = spm_unit("spm_unit_size", period.this_year)
        capped_size = clip(size, 2, p.max_group_size)
        state_group = spm_unit.household("state_group_str", period.this_year)
        state = spm_unit.household("state_code_str", period.this_year)
        monthly_fpg = fpg(capped_size, state_group, period, parameters) / MONTHS_IN_YEAR
        monthly_smi = smi(capped_size, state, period, parameters) / MONTHS_IN_YEAR
        enrolled = add(spm_unit, period.this_year, ["is_enrolled_in_ccdf"]) > 0
        initial_limit = np.ceil(monthly_fpg * p.income.fpl_rate.initial)
        ongoing_limit = max_(
            np.ceil(monthly_fpg * p.income.fpl_rate.ongoing),
            np.ceil(monthly_smi * p.income.smi_rate.ongoing),
        )
        return expanded_child_welfare | (
            countable_income < where(enrolled, ongoing_limit, initial_limit)
        )
