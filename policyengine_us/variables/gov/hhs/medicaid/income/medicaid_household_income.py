from policyengine_us.model_api import *


class medicaid_household_income(Variable):
    value_type = float
    entity = Person
    label = "Medicaid MAGI household income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/42/435.603#d"

    def formula(person, period, parameters):
        child = person("medicaid_non_filer_child_age_eligible", period)
        non_filer_rules = person("medicaid_uses_non_filer_rules", period)
        member_income = person("medicaid_household_income_member", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period).astype(int)
        head_spouse_income = person.tax_unit.sum(head_or_spouse * member_income)
        same_unit_spouse_income = head_or_spouse * head_spouse_income - (
            head_or_spouse * member_income
        )
        cohabitating_separate = person.tax_unit("cohabitating_spouses", period) & (
            person.tax_unit("head_spouse_count", period) == 1
        )
        separate_spouse_income = where(
            cohabitating_separate
            & (
                person("is_tax_unit_head_or_spouse", period)
                | person("claimed_as_dependent_on_another_return", period)
            ),
            person.marital_unit.sum(member_income) - member_income,
            0,
        )
        spouse_income = same_unit_spouse_income + separate_spouse_income
        family_child_income = person.family.sum(
            person("medicaid_non_filer_child_age_eligible", period) * member_income
        )
        family_parent_income = person.family.sum(
            person("is_parent", period) * member_income
        )
        non_filer_household_income = where(
            child,
            spouse_income + family_parent_income + family_child_income,
            member_income + spouse_income + family_child_income,
        )
        tax_household_income = (
            person.tax_unit.sum(member_income) + separate_spouse_income
        )

        return where(non_filer_rules, non_filer_household_income, tax_household_income)
