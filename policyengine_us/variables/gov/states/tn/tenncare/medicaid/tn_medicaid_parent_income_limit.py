from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class tn_medicaid_parent_income_limit(Variable):
    value_type = float
    entity = Person
    label = "Tennessee Medicaid parent income limit"
    default_value = 0
    documentation = (
        "Tennessee applies this parent and caretaker relative income limit as a "
        "share of the federal poverty guideline, including the five-point "
        "MAGI disregard, during the historical dollar-schedule period. "
        "The variable returns zero outside that period."
    )
    unit = "/1"
    definition_period = YEAR
    defined_for = StateCode.TN
    reference = (
        "https://www.medicaid.gov/State-resource-center/Medicaid-State-Plan-Amendments/Downloads/TN/TN-14-0005.pdf#page=19",
        "https://www.ecfr.gov/current/title-42/section-435.603#p-435.603(d)(4)",
    )

    def formula(person, period, parameters):
        parent = parameters(period).gov.states.tn.tenncare.medicaid.parent
        p = parent.income_limit
        disregard = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.parent.fpl_disregard
        size = person("medicaid_household_size", period)
        capped_size = min_(size, p.max_household_size).astype(int)
        additional_people = max_(size - p.max_household_size, 0)
        monthly_limit = p.amount[capped_size] + additional_people * p.additional_person
        state_group = person.household("state_group_str", period)
        return parent.in_effect * (
            monthly_limit * MONTHS_IN_YEAR / fpg(size, state_group, period, parameters)
            + disregard
        )
