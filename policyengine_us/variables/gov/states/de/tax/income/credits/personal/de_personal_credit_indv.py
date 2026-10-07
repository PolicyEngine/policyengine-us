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
        # dependent split, so the optimal one is the tax-minimising one,
        # including the EITC applied afterwards (Line 34).
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

        # PIT-RES Line 34 applies the non-refundable EITC only to the column
        # of the spouse with the higher Line 23 taxable income; with equal
        # incomes either column qualifies.
        taxable = person("de_taxable_income_indv", period)
        head_taxable = person.tax_unit.sum(is_head * taxable)
        spouse_taxable = person.tax_unit.sum(is_spouse * taxable)

        # Try every split of the dependent increments. Keep the one that uses
        # the most credits, then the one that leaves the most tax in the
        # column the EITC can reduce. Both criteria treat the spouses alike,
        # so the result does not depend on which one is labelled head, and
        # together they minimise the column taxes after the EITC.
        best_n = np.zeros_like(head_capacity)
        best_used = np.full_like(head_capacity, -np.inf)
        best_eitc_room = np.full_like(head_capacity, -np.inf)
        for n in range(int(dep_units.max(initial=0)) + 1):
            valid = n <= dep_units
            head_used = min_(n * credit_per, head_capacity)
            spouse_used = min_((dep_units - n) * credit_per, spouse_capacity)
            used = head_used + spouse_used
            head_room = head_capacity - head_used
            spouse_room = spouse_capacity - spouse_used
            eitc_room = select(
                [head_taxable > spouse_taxable, head_taxable < spouse_taxable],
                [head_room, spouse_room],
                max_(head_room, spouse_room),
            )
            better = valid & (
                (used > best_used)
                | ((used == best_used) & (eitc_room > best_eitc_room))
            )
            best_n = where(better, n, best_n)
            best_used = where(better, used, best_used)
            best_eitc_room = where(better, eitc_room, best_eitc_room)

        head_alloc = credit_per + best_n * credit_per
        spouse_alloc = credit_per + (dep_units - best_n) * credit_per

        return is_head_or_spouse * where(is_head, head_alloc, spouse_alloc)
