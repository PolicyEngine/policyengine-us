from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.income._claiming_tax_unit import (
    medicaid_claiming_tax_unit_value,
    medicaid_external_claimed_sum,
)


class ca_medicaid_household_pregnancies(Variable):
    value_type = int
    entity = Person
    label = "Unborn children in the California Medi-Cal MAGI household"
    documentation = (
        "The number of children expected by every pregnant member of the "
        "person's MAGI Medi-Cal household, including the person. California "
        "elects the 42 CFR 435.603(b) option to count a pregnant member as "
        "herself plus the children she expects when sizing other members' "
        "households."
    )
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = (
        # ACWDL 20-10: the unborn children of a pregnant tax filer, spouse, or tax
        # dependent belong to each member's household composition.
        "https://www.dhcs.ca.gov/wp-content/uploads/2025/10/c20-10.pdf#page=3",
        # DHCS MAGI household size flow chart, step 8: add the children expected
        # by every other pregnant member of the composition.
        "https://www.dhcs.ca.gov/hy/wp-content/uploads/2025/10/MAGIHouseholdSizeFlowChartADA.pdf#page=3",
    )

    def formula(person, period, parameters):
        # Follow the applicant's MAGI composition, not the entire residence.
        # This parallels medicaid_household_size, with pregnancies as weights.
        pregnancies = person("current_pregnancies", period)
        child = person("medicaid_non_filer_child_age_eligible", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        head_spouse_pregnancies = person.tax_unit.sum(head_or_spouse * pregnancies)
        same_unit_spouse = head_or_spouse * (head_spouse_pregnancies - pregnancies)
        cohabitating_separate = person.tax_unit("cohabitating_spouses", period) & (
            person.tax_unit("head_spouse_count", period) == 1
        )
        outside_claim = person("claimed_as_dependent_on_another_return", period)
        separate_spouse = where(
            cohabitating_separate & (head_or_spouse | outside_claim),
            person.marital_unit.sum(pregnancies) - pregnancies,
            0,
        )
        spouse_pregnancies = same_unit_spouse + separate_spouse
        is_parent = person("is_parent", period)
        child_pregnancies = person.family.sum(child * pregnancies)
        # ACWDL 20-10 non-filer rule for a child-age applicant: the household is
        # the child, the child's children, the parents in the home, and the
        # siblings. Sum once over the UNION of child-age members and parents so
        # a pregnant member who is both child-age and a parent (a teen mother)
        # contributes her pregnancies once, not once per role.
        child_household_pregnancies = person.family.sum(
            (child | is_parent) * pregnancies
        )
        branch_pregnancies = where(
            child,
            child_household_pregnancies,
            pregnancies + child_pregnancies,
        )

        # The spouse channel above must not re-count a spouse who already sits
        # inside the branch's family sum. Derive the spouse's child-age and
        # parent flags through the same two channels (same tax unit head/spouse;
        # cohabitating separate filers via the marital unit). This assumes
        # spouses share the family entity, so a spouse inside the branch mask
        # is already counted by the family sum.
        def spouse_has_flag(flag):
            flag = flag.astype(int)
            same_unit = head_or_spouse * (
                person.tax_unit.sum(head_or_spouse * flag) - flag
            )
            separate = where(
                cohabitating_separate & (head_or_spouse | outside_claim),
                person.marital_unit.sum(flag) - flag,
                0,
            )
            return (same_unit + separate) > 0

        spouse_child = spouse_has_flag(child)
        spouse_parent = spouse_has_flag(is_parent)
        spouse_in_branch = where(child, spouse_child | spouse_parent, spouse_child)
        non_filer_pregnancies = (
            branch_pregnancies + spouse_pregnancies * ~spouse_in_branch
        )

        # Include a separately filing spouse for every member of this tax
        # household, including dependents whose own marital unit is a singleton.
        tax_pregnancies = person.tax_unit.sum(
            pregnancies + head_or_spouse * separate_spouse
        )
        tax_pregnancies += medicaid_external_claimed_sum(
            person, period, person.tax_unit("tax_unit_id", period), pregnancies
        ).astype(int)
        claimant_pregnancies = medicaid_claiming_tax_unit_value(
            person, period, tax_pregnancies
        ).astype(int)
        return where(
            person("medicaid_uses_non_filer_rules", period),
            non_filer_pregnancies,
            where(
                person("medicaid_has_known_claiming_tax_unit", period),
                claimant_pregnancies,
                tax_pregnancies,
            ),
        )
