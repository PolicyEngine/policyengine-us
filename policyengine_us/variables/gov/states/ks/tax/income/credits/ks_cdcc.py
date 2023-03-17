from policyengine_us.model_api import *


class ks_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "KS Child and Dependent Care Expenses Credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ksrevenue.gov/pdf/k-4021.pdf"
        "https://www.ksrevenue.gov/pdf/ip21.pdf"
        "https://www.ksrevenue.gov/pdf/k-4022.pdf"
        "https://www.ksrevenue.gov/pdf/ip22.pdf"
    )
    defined_for = StateCode.KS

    """
    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ca.tax.income.credits.child_dependent_care
        agi = tax_unit("adjusted_gross_income", period)
        federal_cdcc = tax_unit("cdcc", period)
        multiplier_1 = p.multiplier_1.calc(agi)
        multiplier_2 = p.multiplier_2.calc(agi)
        return federal_cdcc * multiplier_1 * multiplier_2
    """
