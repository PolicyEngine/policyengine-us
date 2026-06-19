from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.income._claiming_tax_unit import (
    medicaid_claiming_tax_unit_sum,
    medicaid_external_claimed_sum,
)


class medicaid_household_income(Variable):
    value_type = float
    entity = Person
    label = "Medicaid MAGI household income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/42/435.603#d"

    def formula(person, period, parameters):
        child_age_eligible = person("medicaid_non_filer_child_age_eligible", period)
        non_filer_rules = person("medicaid_uses_non_filer_rules", period)
        member_income = person("medicaid_household_income_member", period)
        required_to_file = person("medicaid_person_is_required_to_file", period)
        non_filing_dependent = person("medicaid_is_tax_dependent", period) & (
            ~required_to_file
        )
        tax_member_income = where(
            non_filing_dependent,
            0,
            person("medicaid_magi_person", period),
        )
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        head_or_spouse_count = head_or_spouse.astype(int)
        head_spouse_income = person.tax_unit.sum(head_or_spouse_count * member_income)
        same_unit_spouse_income = head_or_spouse_count * head_spouse_income - (
            head_or_spouse_count * member_income
        )
        cohabitating_separate = person.tax_unit("cohabitating_spouses", period) & (
            person.tax_unit("head_spouse_count", period) == 1
        )
        claimed_by_another_return = person(
            "claimed_as_dependent_on_another_return", period
        )
        separate_spouse_income = where(
            cohabitating_separate & (head_or_spouse | claimed_by_another_return),
            person.marital_unit.sum(member_income) - member_income,
            0,
        )
        spouse_income = same_unit_spouse_income + separate_spouse_income
        family_child_income = person.family.sum(child_age_eligible * member_income)
        family_parent_income = person.family.sum(
            person("is_parent", period) * member_income
        )
        non_filer_household_income = where(
            child_age_eligible,
            spouse_income + family_parent_income + family_child_income,
            member_income + spouse_income + family_child_income,
        )
        tax_household_income = (
            person.tax_unit.sum(tax_member_income) + separate_spouse_income
        )
        tax_household_income = tax_household_income + medicaid_external_claimed_sum(
            person,
            period,
            person.tax_unit("tax_unit_id", period),
            tax_member_income,
        )
        known_claiming_tax_unit = person("medicaid_has_known_claiming_tax_unit", period)
        claimant_tax_household_income = medicaid_claiming_tax_unit_sum(
            person, period, tax_member_income
        )

        return where(
            non_filer_rules,
            non_filer_household_income,
            where(
                known_claiming_tax_unit,
                claimant_tax_household_income,
                tax_household_income,
            ),
        )
