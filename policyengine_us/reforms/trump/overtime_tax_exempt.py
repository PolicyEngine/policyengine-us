from policyengine_us.model_api import *


def create_trump_overtime_tax_exempt() -> Reform:
    class taxable_income(Variable):
        value_type = float
        entity = TaxUnit
        label = "IRS taxable income"
        unit = USD
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            agi = tax_unit("adjusted_gross_income", period)
            overtime_hours = add(
                tax_unit, period, ["irs_overtime_employment_income"]
            )
            total_agi = max_(0, agi - overtime_hours)
            exemptions = tax_unit("exemptions", period)
            deductions = tax_unit("taxable_income_deductions", period)
            return max_(0, total_agi - exemptions - deductions)

    class reform(Reform):
        def apply(self):
            self.update_variable(taxable_income)

    return reform


def create_trump_overtime_tax_exempt_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_trump_overtime_tax_exempt()

    p = parameters(period).gov.contrib.trump.overtime_tax_exempt

    if p.in_effect:
        return create_trump_overtime_tax_exempt()
    else:
        return None


overtime_tax_exempt = create_trump_overtime_tax_exempt_reform(
    None, None, bypass=True
)
