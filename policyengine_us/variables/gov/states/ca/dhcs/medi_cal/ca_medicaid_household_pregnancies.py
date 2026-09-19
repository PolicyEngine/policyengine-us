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
        child_pregnancies = person.family.sum(child * pregnancies)
        parent_pregnancies = person.family.sum(
            person("is_parent", period) * pregnancies
        )
        non_filer_pregnancies = spouse_pregnancies + where(
            child,
            parent_pregnancies + child_pregnancies,
            pregnancies + child_pregnancies,
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
