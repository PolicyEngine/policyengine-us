from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class mo_mhf_parent_income_limit(Variable):
    value_type = float
    entity = Person
    label = "Missouri MHF parent income limit"
    unit = "/1"
    definition_period = YEAR
    defined_for = StateCode.MO
    reference = "https://dssmanuals.mo.gov/family-mo-healthnet-magi/1810-000-00/1810-020-00/1810-020-10/"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mo.dss.mhf.income_limit
        size = person("medicaid_household_size", period)
        capped_size = min_(size, p.max_household_size).astype(int)
        additional_people = max_(size - p.max_household_size, 0)

        monthly_limit = (
            p.amount[capped_size]
            + additional_people * p.additional_person
        )
        annual_limit = monthly_limit * MONTHS_IN_YEAR
        state_group = person.household("state_group_str", period)
        return annual_limit / fpg(size, state_group, period, parameters)
