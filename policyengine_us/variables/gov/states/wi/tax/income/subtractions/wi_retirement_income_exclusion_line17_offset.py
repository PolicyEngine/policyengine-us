from policyengine_us.model_api import *


class wi_retirement_income_exclusion_line17_offset(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin retirement subtraction lost when the larger exclusion is claimed"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/05/6/b/54",
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/05/6/b/54m/c",
        # PDF pages 7-8
        "https://www.revenue.wi.gov/TaxForms2025/2025-ScheduleSB-Inst.pdf#page=7",
    )
    defined_for = "wi_retirement_income_exclusion_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.wi.tax.income.subtractions.retirement_income
        person = tax_unit.members
        age = person("age", period)
        retirement = add(person, period, p.sources)
        eligible16 = (age >= p.exclusion.min_age) & person(
            "is_tax_unit_head_or_spouse", period
        )
        retirement16 = retirement * eligible16
        line16_person = min_(p.exclusion.max_amount.single, retirement16)

        # Use the same qualifying income sources as both existing retirement
        # subtractions, removing amounts claimed on line 16 (worksheet step 4).
        eligible17 = (age >= p.min_age) & ~person("is_tax_unit_dependent", period)
        line17_person = min_(p.max_amount, retirement * eligible17) * tax_unit.project(
            tax_unit("wi_retirement_income_subtraction_agi_eligible", period)
        )
        remaining = max_(0, retirement - line16_person)
        nonpooled_offset = tax_unit.sum(line17_person - min_(line17_person, remaining))

        filing_status = tax_unit("filing_status", period)
        pooled = (filing_status == filing_status.possible_values.JOINT) & (
            tax_unit.sum(eligible16) >= 2
        )
        # The joint limit is pooled regardless of each spouse's income. Assign
        # line 16 to income above the existing line 17 entitlements first; no
        # proportional allocation is required by the statute or worksheet.
        pooled_line17 = tax_unit.sum(line17_person * eligible16)
        pooled_remaining = max_(
            0,
            tax_unit.sum(retirement16)
            - tax_unit("wi_retirement_income_exclusion_amount", period),
        )
        pooled_offset = max_(0, pooled_line17 - pooled_remaining)
        offset = where(pooled, pooled_offset, nonpooled_offset)
        # Only add back subtraction actually included in the standard return.
        return min_(offset, tax_unit("wi_retirement_income_subtraction", period))
