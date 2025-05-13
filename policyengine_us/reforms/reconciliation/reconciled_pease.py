from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_reconciled_pease() -> Reform:
    class itemized_taxable_income_deductions_reduction(Variable):
        value_type = float
        entity = TaxUnit
        label = "Itemized taxable income deductions reduction"
        unit = USD
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.reconciliation.pease
            if p.in_effect:
                filing_status = tax_unit("filing_status", period)
                top_rate_threshold = parameters(
                    period
                ).gov.irs.income.bracket.thresholds["6"][filing_status]
                agi = tax_unit("adjusted_gross_income", period)
                exemptions = tax_unit("exemptions", period)
                taxable_income = max_(0, agi - exemptions)
                taxable_income_excess = max_(
                    0, taxable_income - top_rate_threshold
                )
                total_itemized_deductions = tax_unit(
                    "total_itemized_taxable_income_deductions", period
                )
                lesser_of_deductions_or_excess = min_(
                    total_itemized_deductions, taxable_income_excess
                )
                return p.rate * lesser_of_deductions_or_excess
            return 0

    class reform(Reform):
        def apply(self):
            self.update_variable(itemized_taxable_income_deductions_reduction)

    return reform


def create_reconciled_pease_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_reconciled_pease()

    p = parameters.gov.contrib.reconciliation.pease

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_reconciled_pease()
    else:
        return None


reconciled_pease = create_reconciled_pease_reform(None, None, bypass=True)
