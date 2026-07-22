from policyengine_us.model_api import *


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
        # columns. We allocate the dependent increments to maximise total
        # credits used (i.e. minimise tax); the taxpayer may choose any
        # dependent split, so the optimal one is the tax-minimising one.
        p = parameters(period).gov.states.de.tax.income.credits
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        is_head_or_spouse = is_head | is_spouse

        credit_per = p.personal_credits.personal
        person_tax = person("de_income_tax_before_non_refundable_credits_indv", period)
        head_tax = person.tax_unit.sum(is_head * person_tax)
        spouse_tax = person.tax_unit.sum(is_spouse * person_tax)

        fixed = person("de_aged_personal_credit_indv", period) + person(
            "de_cdcc_indv", period
        )
        # Each column's own $110 personal credit is fixed to that column.
        head_fixed = person.tax_unit.sum(is_head * fixed) + credit_per
        spouse_fixed = person.tax_unit.sum(is_spouse * fixed) + credit_per

        head_capacity = max_(head_tax - head_fixed, 0)
        spouse_capacity = max_(spouse_tax - spouse_fixed, 0)

        total_units = person.tax_unit("exemptions_count", period)
        # Dependent increments: exemptions beyond the two spouses.
        dep_units = max_(total_units - 2, 0)

        # Optimal dependent split: try proportional floor and ceil, pick
        # whichever maximises effective credits (min of alloc vs
        # remaining capacity in each column).
        total_capacity = head_capacity + spouse_capacity
        ratio = where(total_capacity > 0, head_capacity / total_capacity, 0)

        n_low = np.floor(dep_units * ratio)
        n_high = n_low + 1
        n_low = max_(min_(n_low, dep_units), 0)
        n_high = max_(min_(n_high, dep_units), 0)

        eff_low = min_(n_low * credit_per, head_capacity) + min_(
            (dep_units - n_low) * credit_per, spouse_capacity
        )
        eff_high = min_(n_high * credit_per, head_capacity) + min_(
            (dep_units - n_high) * credit_per, spouse_capacity
        )

        n_head_dep = where(eff_high > eff_low, n_high, n_low)
        head_alloc = credit_per + n_head_dep * credit_per
        spouse_alloc = credit_per + (dep_units - n_head_dep) * credit_per

        return is_head_or_spouse * where(is_head, head_alloc, spouse_alloc)
