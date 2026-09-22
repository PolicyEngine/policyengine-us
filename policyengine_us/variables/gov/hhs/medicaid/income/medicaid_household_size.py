from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.income._claiming_tax_unit import (
    medicaid_claiming_tax_unit_value,
    medicaid_external_claimed_sum,
)


class medicaid_household_size(Variable):
    value_type = int
    entity = Person
    label = "Medicaid MAGI household size"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/42/435.603#b",
        "https://www.law.cornell.edu/cfr/text/42/435.603#f",
        # California (ACWDL 20-10) counts the unborn children of every member of
        # the applicant's MAGI household; see ca_medicaid_household_pregnancies.
        "https://www.dhcs.ca.gov/wp-content/uploads/2025/10/c20-10.pdf#page=3",
    )

    def formula(person, period, parameters):
        child_age_eligible = person("medicaid_non_filer_child_age_eligible", period)
        non_filer_rules = person("medicaid_uses_non_filer_rules", period)
        family_child_count = person.family.sum(child_age_eligible)
        family_parent_count = person.family.sum(person("is_parent", period))
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        same_unit_spouse_count = head_or_spouse.astype(int) * (
            person.tax_unit("head_spouse_count", period) - 1
        )
        cohabitating_separate = person.tax_unit("cohabitating_spouses", period) & (
            person.tax_unit("head_spouse_count", period) == 1
        )
        claimed_by_another_return = person(
            "claimed_as_dependent_on_another_return", period
        )
        separate_spouse_count = (head_or_spouse | claimed_by_another_return).astype(
            int
        ) * cohabitating_separate.astype(int)
        spouse_count = same_unit_spouse_count + separate_spouse_count
        non_filer_household_size = where(
            child_age_eligible,
            spouse_count + family_parent_count + family_child_count,
            1 + spouse_count + family_child_count,
        )
        tax_household_size = person.tax_unit("tax_unit_size", period) + (
            cohabitating_separate.astype(int)
        )
        person_count = np.ones_like(person.tax_unit("tax_unit_id", period))
        tax_household_size = tax_household_size + medicaid_external_claimed_sum(
            person,
            period,
            person.tax_unit("tax_unit_id", period),
            person_count,
        ).astype(int)
        known_claiming_tax_unit = person("medicaid_has_known_claiming_tax_unit", period)
        claimant_tax_household_size = medicaid_claiming_tax_unit_value(
            person, period, tax_household_size
        ).astype(int)

        # California counts the unborn children of all members included in the
        # applicant's MAGI household. Preserve the existing treatment elsewhere.
        state = person.household("state_code", period)
        pregnancies = where(
            state == StateCode.CA,
            person("ca_medicaid_household_pregnancies", period),
            person("current_pregnancies", period),
        )
        return (
            where(
                non_filer_rules,
                non_filer_household_size,
                where(
                    known_claiming_tax_unit,
                    claimant_tax_household_size,
                    tax_household_size,
                ),
            )
            + pregnancies
        )
