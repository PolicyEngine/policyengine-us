from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.de.tax.income.de_combined_separate_credits import (
    de_combined_separate_credit_choices,
)


class de_personal_credit_indv(Variable):
    value_type = float
    entity = Person
    label = "Delaware personal credit per person for combined separate filing"
    unit = USD
    definition_period = YEAR
    reference = "https://revenuefiles.delaware.gov/2025/PITForms_Instructions/Instructions/PIT-RES_Instructions_2025-01.pdf#page=8"
    defined_for = StateCode.DE

    def formula(person, period, parameters):
        # PIT-RES Line 27a: "split the total between Columns A and B in
        # increments of $110." The instructions' example pins down how:
        # a married couple with no dependents enters "$110 in each column
        # if Filing Status 4" - each spouse's own credit belongs to their
        # own column, and only the DEPENDENT credits may be split between
        # columns. The taxpayer may choose any dependent split; it is chosen
        # together with the Line 31 and Line 34 columns to minimise tax (see
        # de_combined_separate_credit_choices).
        p = parameters(period).gov.states.de.tax.income.credits
        credit_per = p.personal_credits.personal
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        dep_units = max_(person.tax_unit("exemptions_count", period) - 2, 0)
        head_dep, _, _ = de_combined_separate_credit_choices(
            person.tax_unit, period, parameters
        )
        head_alloc = credit_per + head_dep * credit_per
        spouse_alloc = credit_per + (dep_units - head_dep) * credit_per
        return where(is_head, head_alloc, where(is_spouse, spouse_alloc, 0))
