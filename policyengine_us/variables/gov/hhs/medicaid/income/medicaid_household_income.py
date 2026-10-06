from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.income._claiming_tax_unit import (
    medicaid_claiming_tax_unit_value,
    medicaid_external_claimed_sum,
)


class medicaid_household_income(Variable):
    value_type = float
    entity = Person
    label = "Medicaid MAGI household income"
    unit = USD
    documentation = (
        "The sum of the MAGI-based income of every member of the person's "
        "Medicaid household (42 CFR 435.603(d)(1)). Members' amounts are "
        "added before any floor, so a loss of one member, such as a spouse's "
        "business loss on a joint return, offsets the others' income, as it "
        "does in the couple's joint AGI. Only the total is floored at zero, "
        "as Form 8962 combines the taxpayer's and dependents' modified AGIs "
        "'even if one or both of them are negative' before entering a "
        "negative total as zero. In the non-filer household, whose parents "
        "and siblings are read from the whole family, those relatives' "
        "amounts are added only when positive (each child's, and each "
        "couple's parents' netted), so a relative outside the household "
        "cannot lower its income. An adult's own amount and their spouse's "
        "are added signed; a child's own amount and their siblings' enter "
        "with the family's children, only when positive. Unmarried "
        "co-resident parents are each counted only when positive."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/42/435.603#d",
        "https://www.law.cornell.edu/uscode/text/26/36B#d_2_A",
        "https://www.irs.gov/pub/irs-prior/i8962--2025.pdf#page=8",
    )

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
        # The non-filer household's parents and siblings are read from the
        # whole family, which can include people outside the household, such
        # as a grandparent who is also a parent there. So their amounts are
        # added only when positive: each child's, and each couple's parents'
        # netted together, so married parents' losses still offset each
        # other's income. An adult's own and their spouse's amounts are added
        # signed; a child's own amount is among the family's children.
        family_child_income = person.family.sum(
            child_age_eligible * max_(0, member_income)
        )
        is_parent = person("is_parent", period)
        couple_parent_income = person.marital_unit.sum(is_parent * member_income)
        couple_parents = person.marital_unit.sum(is_parent)
        parent_share = np.divide(
            is_parent.astype(float),
            couple_parents,
            out=np.zeros_like(couple_parents, dtype=float),
            where=couple_parents > 0,
        )
        family_parent_income = person.family.sum(
            parent_share * max_(0, couple_parent_income)
        )
        non_filer_household_income = where(
            child_age_eligible,
            spouse_income + family_parent_income + family_child_income,
            member_income + spouse_income + family_child_income,
        )
        # A tax household includes the cohabiting spouse of a filer who files
        # separately (42 CFR 435.603(f)(4)), and so do the households of that
        # filer's dependents, which are the filer's (435.603(f)(2)).
        filer_separate_spouse_income = where(
            head_or_spouse | claimed_by_another_return,
            separate_spouse_income,
            person.tax_unit.sum(
                person("is_tax_unit_head", period) * separate_spouse_income
            ),
        )
        tax_household_income = (
            person.tax_unit.sum(tax_member_income) + filer_separate_spouse_income
        )
        tax_household_income = tax_household_income + medicaid_external_claimed_sum(
            person,
            period,
            person.tax_unit("tax_unit_id", period),
            tax_member_income,
        )
        known_claiming_tax_unit = person("medicaid_has_known_claiming_tax_unit", period)
        claimant_tax_household_income = medicaid_claiming_tax_unit_value(
            person, period, tax_household_income
        )

        household_income = where(
            non_filer_rules,
            non_filer_household_income,
            where(
                known_claiming_tax_unit,
                claimant_tax_household_income,
                tax_household_income,
            ),
        )
        # Each member's MAGI-based income can be negative; only the
        # household's total is floored.
        return max_(0, household_income)
