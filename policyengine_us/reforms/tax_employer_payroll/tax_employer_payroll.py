from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def tax_employer_payroll_reform() -> Reform:
    """
    General workflow for creating reform:
    1. Make a boolean for the reform under parameters/contrib/{reform_name}
    called in_effect.
    2. Create new variables if necessary.
    3. Redefine rule for calculating existing variable (in this case social
    security taxation).
    4. Add this reform to reforms/reforms.py.
    """

    """
    Create a variable with the same name as the variable we are trying to 
    amend.
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
    """

    class irs_gross_income(Variable):
        # The input is Variable because policyengine.core functions(?) will
        # find the variables we name and feed it into this class

        # The following are attributes copied from the .../irs_gross_income.py
        value_type = float
        entity = Person
        label = "Gross income"
        unit = USD
        documentation = "Gross income as defined in the Internal Revenue Code."
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/61"

        # the formula is also copied from the .../irs_gross_income.py
        def formula(person, period, parameters):
            sources = parameters(period).gov.irs.gross_income.sources
            total = 0
            not_dependent = ~person("is_tax_unit_dependent", period)
            for source in sources:
                # Add positive values only - losses are deducted later.
                total += not_dependent * max_(0, add(person, period, [source]))

            # Here we add in the employer side contribution

            # Note that each reform correspond to a boolean specified under
            # "policyengine_us/parameters/gov/contrib/"
            # I create a directory there of the same name
            # as this file's parent directory ("tax_employer_payroll")
            # Inside it is a yaml file called in_effect.yaml that is
            # a boolean, set to false.
            # (We'll set it to true later)
            p = parameters(period).gov.contrib.tax_employer_payroll

            # note that we created two new variables for the purpose of this
            # reform
            # they respectively measure the amount paid by the employer to a
            # person for:
            # (i) social security and (ii) medicare.
            # they are under "variables/gov/irs/tax/payroll/social_security
            # /employer_social_security_tax.py"
            # and "policyengine_us/variables/gov/irs/tax/payroll/medicare/
            # employer_medicare_tax.py"
            # We refer to them with the person method(?), which has the
            # following syntax
            employer_contribution = person(
                "employer_social_security_tax", period
            ) + person("employer_medicare_tax", period)

            # Update total to include employer_contribution
            total += employer_contribution

            return total

    # the reform class contains a custom method that refers
    # to the updated variable
    class reform(Reform):
        # these are all custom methods
        def apply(self):
            self.update_variable(irs_gross_income)

    return reform


def create_tax_employer_payroll_reform(parameters, period, bypass: bool = False):
    # Create a create_{reform name} function that initializes the reform object
    # There are two sufficient conditions for this function to return
    # the reform

    # 1. If bypass is set to true
    if bypass is True:
        return tax_employer_payroll_reform()

    # 2. If boolean in in_effect.yaml is set to true
    path = parameters(period).gov.contrib.tax_employer_payroll
    current_period = period_(period)
    reform_active = False

    for i in range(5):
        if path(current_period).in_effect:
            # If in any of the next five years, the boolean is true,
            # set the boolean reform_active to true, and stop the check,
            # i.e., assume the reform is active in all subsequent years.
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    # if the loop set reform_active to true, return the reform.
    if reform_active:
        return tax_employer_payroll_reform()
    else:
        return None


# Create a reform object to by setting bypass to true,
# for the purpose of running tests
tax_employer_payroll_reform = create_tax_employer_payroll_reform(
    None, None, bypass=True
)
