from policyengine_us.model_api import *


class savers_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Retirement Savings Credit"
    unit = USD
    reference = (
        "https://www.irs.gov/pub/irs-pdf/f8880.pdf",
        "https://www.law.cornell.edu/uscode/text/26/25B#c",
    )

    def formula(tax_unit, period, parameters):
        credit_limit = tax_unit("savers_credit_credit_limit", period)
        potential = tax_unit("savers_credit_potential", period)
        return min_(credit_limit, potential)
