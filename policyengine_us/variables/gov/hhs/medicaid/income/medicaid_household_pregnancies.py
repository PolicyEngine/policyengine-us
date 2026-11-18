from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.income._household_sum import (
    medicaid_household_sum,
)


class medicaid_household_pregnancies(Variable):
    value_type = int
    entity = Person
    label = "Expected children in the Medicaid MAGI household size"
    documentation = (
        "The expected children counted in the person's MAGI household size. "
        "A pregnant woman counts every child she expects in her own household; "
        "another member counts up to the state's election under 42 CFR "
        "435.603(b) for each pregnant woman in their household."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/42/435.603#b",
        "https://www.medicaid.gov/State-resource-center/Medicaid-State-Plan-Amendments/Downloads/CA/CA-13-0023-MM.pdf#page=7",
        "https://www.medicaid.gov/State-resource-center/Medicaid-State-Plan-Amendments/Downloads/NJ/NJ-13-0016-MM3.pdf#page=5",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicaid.household
        state = person.household("state_code_str", period)
        expected = person("current_pregnancies", period)
        # What each pregnant member adds to the other members' households.
        counted = min_(expected, p.pregnant_member_expected_children_cap[state])
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        head_spouse_count = person.tax_unit("head_spouse_count", period)
        joint = head_or_spouse & (head_spouse_count == 2)
        same_unit_spouse = joint * (
            person.tax_unit.sum(head_or_spouse * counted) - counted
        )
        cohabitating_separate = person.tax_unit("cohabitating_spouses", period) & (
            head_spouse_count == 1
        )
        separate_spouse = where(
            cohabitating_separate
            & (
                head_or_spouse
                | person("claimed_as_dependent_on_another_return", period)
            ),
            person.marital_unit.sum(counted) - counted,
            0,
        )
        household = medicaid_household_sum(
            person,
            period,
            counted,
            same_unit_spouse + separate_spouse,
            person.tax_unit.sum(head_or_spouse * separate_spouse),
        )
        # The household sum includes the person's own capped count; her own
        # household counts every child she expects.
        return household + expected - counted
