from policyengine_us.model_api import *


class la_agi_exempt_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana income that is exempt from the adjusted gross income"
    defined_for = StateCode.LA
    unit = USD
    definition_period = YEAR

    # Functions as subtractions.
    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.la.tax.income.exempt_income
        total_exempt_income = add(tax_unit, period, p.sources)
        if p.reduction.in_effect:
            # Option 1
            exempt_income_reduction = p.reduction.rate.calc(
                total_exempt_income
            )
            # Option 2
            agi = tax_unit("adjusted_gross_income", period)
            exempt_income_rate = np.zeros_like(agi)
            mask = agi != 0
            exempt_income_rate[mask] = total_exempt_income[mask] / agi[mask]
            itemizes = tax_unit("tax_unit_itemizes", period)
            itemized_deductions = tax_unit("la_itemized_deductions", period)
            claimed_itemized_deductions = itemizes * itemized_deductions
            fed_tax_deduction = tax_unit("la_federal_tax_deduction", period)
            pre_exempt_income_tax = max_(
                agi - claimed_itemized_deductions - fed_tax_deduction, 0
            )
            income_tax_present = pre_exempt_income_tax > 0
            exempt_income_tax_reduction = (
                pre_exempt_income_tax * exempt_income_rate
            )
            # The smaller of the two options is applied
            smaller_adjustment = min_(
                exempt_income_tax_reduction, exempt_income_reduction
            )
            final_exempt_income_reduction = where(
                income_tax_present, smaller_adjustment, exempt_income_reduction
            )
            return max_(total_exempt_income - final_exempt_income_reduction, 0)
        return total_exempt_income
