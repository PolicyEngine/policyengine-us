from policyengine_us.model_api import *


class la_agi_exempt_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana income that is exempt from the adjusted gross income"
    defined_for = StateCode.LA
    reference = "https://revenue.louisiana.gov/TaxForms/IT540i(2021)%20Instructions.pdf#page=9"
    definition_period = YEAR

    # Functions as subtractions.
    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.la.tax.income.exempt_income
        total_exempt_income = add(tax_unit, period, p.sources)
        if p.reduction.in_effect:
            # Option 1 is to reduce the exempt income by a marginal rate
            reduced_exempt_income = p.reduction.rate.calc(total_exempt_income)
            # Option 2 is to reduce the federal tax deduction by the percentage of
            # exempt income to AGI
            agi = tax_unit("adjusted_gross_income", period)
            exempt_income_rate = np.zeros_like(agi)
            mask = agi != 0
            exempt_income_rate[mask] = total_exempt_income[mask] / agi[mask]
            # The second option only applies if the tax unit has a federal tax deduction
            federal_tax_deduction = tax_unit(
                "la_federal_tax_deduction", period
            )
            federal_tax_deduction_eligible = federal_tax_deduction > 0
            # Multiply the federal tax deduction by the exempt income rate
            reduced_federal_tax_deduction = (
                federal_tax_deduction * exempt_income_rate
            )
            # The smaller of the two options is applied if taxable income exceeds zero
            smaller_adjustment = min_(
                reduced_federal_tax_deduction, reduced_exempt_income
            )
            final_exempt_income_reduction = where(
                federal_tax_deduction_eligible,
                smaller_adjustment,
                reduced_exempt_income,
            )
            return max_(total_exempt_income - final_exempt_income_reduction, 0)
        return total_exempt_income
