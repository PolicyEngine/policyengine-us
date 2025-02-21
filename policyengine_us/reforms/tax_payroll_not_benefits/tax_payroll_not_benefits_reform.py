from policyengine_us.model_api import *

def create_tax_employer_payroll() -> Reform:
    # make a boolean for the reform under parameters/contrib/
    # redefine rule for social security taxation

    # Create a variable with the same name as the variable we are trying to amend.

    # In this case it's "irs_gross_income", as in "policyengine_us/variables/gov/irs/income/taxable_income/adjusted_gross_income/irs_gross_income/irs_gross_income.py"
    # We amend irs_gross_income because the employer-side contributions will go into taxable income...
    # but taxable income is determined at the tax unit level, by summing up all persons' gross income and deducting tax unit's deductions.
    # But since payroll is calculated at the personal level, we want to add each person's employer contribution to each person, thus we add it to gross income.

    # The input is variable because policyengine.core functions(?) will find the variable with the name we specify in this class and feed it into this class
    class irs_gross_income(Variable):

        # The following are attributes copied from the .../irs_gross_income.py
        value_type = float
        entity = Person
        label = "Gross income"
        unit = USD
        documentation = "Gross income, as defined in the Internal Revenue Code."
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

            # Note that each reform correspond to a boolean specified under "policyengine_us/parameters/gov/contrib/"
            # I create a directory there of the same name as this file's parent directory ("tax_payroll_not_benefits")
            # Inside it is a yaml file called tax_employer_payroll.yaml that is a boolean, set to false.
            # (We'll set it to true later)
            p = parameters(period).gov.contrib.tax_payroll_not_benefits

            if p.tax_payroll_not_benefits_reform is True:
                # note that we created two new variables for the purpose of this reform
                # they respectively measure the amount paid by the employer to a person for (i) social security and (ii) medicare
                # they are under "variables/gov/irs/tax/payroll/social_security/employer_social_security_tax.py"
                # and "policyengine_us/variables/gov/irs/tax/payroll/medicare/employer_medicare_tax.py"
                # We refer to them with the person method(?), which has the following syntax
                employer_contribution = person("employer_social_security_tax", period) + person("employer_medicare_tax", period)

                # Update total to include employer_contribution
                total += employer_contribution

            return total




