from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.income._household_sum import (
    medicaid_household_sum,
)


class medicaid_household_size(Variable):
    value_type = int
    entity = Person
    label = "Medicaid MAGI household size"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/42/435.603#b",
        "https://www.law.cornell.edu/cfr/text/42/435.603#f",
    )

    def formula(person, period, parameters):
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        head_spouse_count = person.tax_unit("head_spouse_count", period)
        cohabitating_separate = person.tax_unit("cohabitating_spouses", period) & (
            head_spouse_count == 1
        )
        separate_spouse = cohabitating_separate & (
            head_or_spouse | person("claimed_as_dependent_on_another_return", period)
        )
        spouse_count = head_or_spouse * (head_spouse_count - 1) + separate_spouse
        members = medicaid_household_sum(
            person,
            period,
            np.ones(person.count),
            spouse_count,
            cohabitating_separate.astype(int),
        )
        # 42 CFR 435.603(b) adds the expected children of pregnant members.
        return members + person("medicaid_household_pregnancies", period)
