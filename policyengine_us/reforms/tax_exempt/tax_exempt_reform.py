from policyengine_us.model_api import *


def create_tax_exempt() -> Reform:
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
            exempt_income = 0
            p = parameters(period).gov.contrib.tax_exempt
            if p.tip_income.income_tax_exempt:
                tip_income = person("tip_income", period)
                exempt_income += tip_income
            if p.overtime.income_tax_exempt:
                exempt_income += person("overtime_income", period)
            return max_(total - exempt_income, 0)

    class payroll_tax_gross_wages(Variable):
        value_type = float
        entity = Person
        label = "Gross wages and salaries for payroll taxes"
        definition_period = YEAR
        unit = USD

        def formula(person, period, parameters):
            income = person("irs_employment_income", period)
            p = parameters(period).gov.contrib.tax_exempt
            exempt_income = 0
            if p.tip_income.payroll_tax_exempt:
                exempt_income += person("tip_income", period)
            if p.overtime.payroll_tax_exempt:
                exempt_income += person("overtime_income", period)
            return max_(income - exempt_income, 0)

    class reform(Reform):
        def apply(self):
            self.update_variable(irs_gross_income)
            self.update_variable(payroll_tax_gross_wages)

    return reform


def create_tax_exempt_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_tax_exempt()

    p = parameters(period).gov.contrib.tax_exempt

    if p.in_effect:
        return create_tax_exempt()
    else:
        return None


tax_exempt_reform = create_tax_exempt_reform(None, None, bypass=True)
