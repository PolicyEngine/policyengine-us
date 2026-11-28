from policyengine_us.model_api import *


def payroll_tax_exempt_income(person, period, parameters):
    """Tips and overtime premiums the reform exempts from payroll taxes.

    employer_payroll_tax_fixed_employer_cost_change reads this too, so the
    wages it holds employer cost on are the ones this reform taxes.
    """
    p = parameters(period).gov.contrib.tax_exempt
    exempt_income = 0
    if p.tip_income.payroll_tax_exempt:
        exempt_income += person("tip_income", period)
    if p.overtime.payroll_tax_exempt:
        exempt_income += person("fsla_overtime_premium", period)
    return exempt_income


def tax_exempt_payroll_tax_gross_wages(person, period, parameters):
    """Formula of payroll_tax_gross_wages under the reform.

    It is defined here, rather than in the reform's class, so that
    employer_payroll_tax_fixed_employer_cost_change can tell a system that
    has the reform from one that does not.
    """
    employment_income = person("employment_income", period)
    fica_deductions = person("fica_pre_tax_contributions", period)
    exempt_income = payroll_tax_exempt_income(person, period, parameters)
    income = max_(0, employment_income - fica_deductions)
    return max_(income - exempt_income, 0)


def create_tax_exempt() -> Reform:
    class irs_gross_income(Variable):
        value_type = float
        entity = Person
        label = "Gross income"
        unit = USD
        documentation = "Gross income, as defined in the Internal Revenue Code."
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
                exempt_income += person("fsla_overtime_premium", period)
            return max_(total - exempt_income, 0)

    class payroll_tax_gross_wages(Variable):
        value_type = float
        entity = Person
        label = "Gross wages and salaries for payroll taxes"
        definition_period = YEAR
        unit = USD

        formula = tax_exempt_payroll_tax_gross_wages

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
