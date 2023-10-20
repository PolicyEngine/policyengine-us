from policyengine_us.model_api import *


class va_tax_adjsutment_calculation(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia aged/blind exemption"
    defined_for = StateCode.VA
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=19"

    def formula(tax_unit, period, parameters):
        va_agi = person(va_agi, "period")
        va_agi_total = person.tax_unit.sum(net_income)

        # avoid divide-by-zero warnings when using where() function
        fraction = np.zeros_like(va_agi_total)
        mask = va_agi_total != 0
        fraction[mask] = va_agi[mask] / va_agi_total[mask]

        # if no net income, then assign entirely to head.
        return where(
            total_net_income == 0,
            person("is_tax_unit_head", period),
            fraction,
        )

        is_head = tax_unit(is_tax_unit_head, "period")
        is_spouse = tax_unit(is_tax_unit_spouse, "period")

        heads_fraction = where(is_head, fraction, 0)
        va_agi_head = heads_fraction * va_agi_total

        spouses_fraction = where(is_spouse, fraction, 0)
        va_agi_spouse = spouses_fraction * va_agi_total

        p1 = parameters(period).gov.states.va.tax.income.spouse_head_adjustment
        p = parameters(period).gov.states.va_tax.income
        min_amount = min(
            va_agi_head - va_personal_exemption_head,
            va_agi_spouse - va_personal_exemption_spouse,
        )

        half_of_taxable_income = va_taxable_income / p1.divider
        diff_amount = min_amount - va_taxable_income
        tax_min = min_(min_amount, half_of_taxable_income) * p.rates
        tax_max = max(diff_amount, half_of_taxable_income) * p.rates
        tax_sum = tax_min + tax_max
        return where(
            min_amount > p.threshold
            and va_taxable_income > p.taxable_threshold,
            p1.adjustment_limit,
            round(va_taxable_income * p.rates) - tax_sum,
        )
