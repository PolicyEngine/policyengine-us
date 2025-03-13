from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def tax_employer_payroll_tax_reform() -> Reform:
    """
    General workflow for creating reform:
    1. Make a boolean for the reform under parameters/contrib/{reform name}
    called in_effect.
    2. Create new variables if necessary.
    3. Redefine rule for calculating existing variable (in this case social
    security taxation).
    3a. Add an init file to initialize the create_{reform name}_reform function.
    4. Add this reform to reforms/reforms.py (see previous pull requests for
    syntax).
    5. Add a unit test under tests/contrib/{reform name}
    if the reform is not just modifying a parameter
    5a. Add unit test for new variables under
    tests/baseline/{new variable's path}

    Specific to this reform:
    We want to modify how an existing variable is calculated.
    In this case it's "irs_gross_income", as in:
    "policyengine_us/variables/gov/irs/income/taxable_income/
    adjusted_gross_income/irs_gross_income/irs_gross_income.py"
    We amend irs_gross_income because the employer-side contributions
    will go into taxable income...
    but taxable income is determined at the tax unit level,
    by summing up all persons' gross income
    and deducting tax unit's deductions. But since payroll is calculated at
    the personal level,
    we want to add each person's employer contribution to each person, thus
    we add it to gross income.

    irs_gross_income refers to "parameters/gov/irs/gross_income/sources"
    to determine which sources of income get added into the variable.
    We modify that list by adding the two variables we created for this
    reform: they are employer's payroll taxes for
    (i) social security and (ii) medicare.
    The new variabes are under "variables/gov/irs/tax/payroll
    /social_security/employer_social_security_tax.py"
    and "policyengine_us/variables/gov/irs/tax/payroll/medicare/
    employer_medicare_tax.py"
    """

    class irs_gross_income(Variable):
        value_type = float
        entity = Person
        label = "IRS gross income"
        definition_period = YEAR
        unit = USD

        def formula(person, period, parameters):
            sources = parameters(period).gov.irs.gross_income.sources
            total = 0
            not_dependent = ~person("is_tax_unit_dependent", period)
            for source in sources:
                # Add positive values only - losses are deducted later.
                total += not_dependent * max_(0, add(person, period, [source]))
            return (
                total
                + person("employer_social_security_tax", period)
                + person("employer_medicare_tax", period)
            )

    # Create a reform object applies the method
    # It inherits the Reform class
    class reform(Reform):
        def apply(self):
            self.update_variable(irs_gross_income)

    return reform


def create_tax_employer_payroll_tax_reform(
    parameters, period, bypass: bool = False
):
    # Create a create_{reform name} function that initializes the reform object
    # There are two sufficient conditions for this function to return
    # the reform

    # 1. If bypass is set to true
    if bypass is True:
        return tax_employer_payroll_tax_reform()

    # 2. If boolean in in_effect.yaml is set to true
    parameter = parameters.gov.contrib.crfb.tax_employer_payroll_tax
    current_period = period_(period)
    reform_active = False

    for i in range(5):
        if parameter(current_period).in_effect:
            # If in any of the next five years, the boolean is true,
            # set the boolean reform_active to true, and stop the check,
            # i.e., assume the reform is active in all subsequent years.
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    # if the loop set reform_active to true, return the reform.
    if reform_active:
        return tax_employer_payroll_tax_reform()
    else:
        return None


# Create a reform object to by setting bypass to true,
# for the purpose of running tests
tax_employer_payroll_tax_reform_object = (
    create_tax_employer_payroll_tax_reform(None, None, bypass=True)
)
