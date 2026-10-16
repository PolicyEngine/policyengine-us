from policyengine_us.model_api import *


class nc_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "North Carolina TANF countable earned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NC
    reference = (
        "https://www.ncdhhs.gov/efs-wf-06-2025a2/open#page=18",
        "https://policies.ncdhhs.gov/wp-content/uploads/wf-114_1-2-2024.pdf#page=2",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nc.ncdhhs.tanf
        person = spm_unit.members
        gross_earned = add(person, period, p.income.earned)
        # State Plan Financial Rules 3: the earnings of children are not counted.
        is_child = person("age", period) < p.eligibility.age_limit
        adult_earned = spm_unit.sum(where(is_child, 0, gross_earned))
        # State Plan Financial Rules 6: 27.5% of gross earned income is excluded.
        return adult_earned * (1 - p.income.earned_income_exclusion_rate)
