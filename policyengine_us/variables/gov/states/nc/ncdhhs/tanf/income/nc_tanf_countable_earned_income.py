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
        "http://reports.oah.state.nc.us/ncac/title%2010a%20-%20health%20and%20human%20services/chapter%2071%20-%20adult%20and%20family%20support/subchapter%20w/subchapter%20w%20rules.pdf#page=7",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nc.ncdhhs.tanf
        person = spm_unit.members
        gross_earned = add(person, period, p.income.earned)
        # State Plan Financial Rules 3: all income is counted except the
        # earnings of children and the income of SSI recipients.
        is_child = person("age", period) < p.eligibility.age_limit
        is_ssi_recipient = (person("ssi", period) > 0) | person("receives_ssi", period)
        counted = ~is_child & ~is_ssi_recipient
        countable_earned = spm_unit.sum(where(counted, gross_earned, 0))
        # State Plan Financial Rules 6: 27.5% of gross earned income is excluded.
        return countable_earned * (1 - p.income.earned_income_exclusion_rate)
