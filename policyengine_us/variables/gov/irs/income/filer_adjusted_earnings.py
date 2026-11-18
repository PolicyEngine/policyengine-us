from policyengine_us.model_api import *


class filer_adjusted_earnings(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Filer earned income adjusted for self-employment tax"
    unit = USD
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/32#c_2",
        "https://www.law.cornell.edu/uscode/text/26/402#e_3",
        "https://www.irs.gov/publications/p596",
        "https://www.irs.gov/instructions/i1040gi",
    )

    def formula(tax_unit, period, parameters):
        # adjusted_earnings already leaves out wages that are not includible
        # in federal gross income (IRC 32(c)(2)(A)(i)) and keeps the
        # personal SE-tax adjustment and zero floor. Dependents' earnings
        # belong on their own returns.
        return tax_unit_non_dep_sum("adjusted_earnings", tax_unit, period)
