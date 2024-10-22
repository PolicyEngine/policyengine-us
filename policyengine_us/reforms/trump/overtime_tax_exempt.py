from policyengine_us.model_api import *


def create_trump_overtime_tax_exempt() -> Reform:
    class irs_gross_income(Variable):
        value_type = float
        entity = Person
        label = "Gross income"
        unit = USD
        documentation = (
            "Gross income, as defined in the Internal Revenue Code."
        )
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/61"

        def formula(person, period, parameters):
            sources = parameters(period).gov.irs.gross_income.sources
            total = 0
            not_dependent = ~person("is_tax_unit_dependent", period)
            for source in sources:
                # Add positive values only - losses are deducted later.
                total += not_dependent * max_(0, add(person, period, [source]))
            overtime_income = person("overtime_income", period)
            return max_(total - overtime_income, 0)

    class payroll_tax_gross_wages(Variable):
        value_type = float
        entity = Person
        label = "Gross wages and salaries for payroll taxes"
        definition_period = YEAR
        unit = USD

        def formula(person, period, parameters):
            income = person("irs_employment_income", period)
            overtime_income = person("overtime_income", period)
            return max_(income - overtime_income, 0)

    class overtime_income(Variable):
        value_type = float
        entity = Person
        label = "Income from overtime hours worked"
        unit = USD
        definition_period = YEAR

    class reform(Reform):
        def apply(self):
            self.update_variable(irs_gross_income)
            self.update_variable(overtime_income)
            self.update_variable(payroll_tax_gross_wages)

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
