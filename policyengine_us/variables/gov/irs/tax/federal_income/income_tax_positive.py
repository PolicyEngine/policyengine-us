from policyengine_us.model_api import *


class income_tax_positive(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    unit = USD
    label = "Federal income tax (non-negative)"
    documentation = (
        "Federal income tax liability, floored at zero. This matches the CBO "
        "definition of income tax receipts, where refundable credit payments "
        "in excess of tax liability are classified as outlays rather than "
        "negative receipts."
    )
    reference = "https://www.cbo.gov/publication/43767"

    def formula(tax_unit, period, parameters):
        income_tax = tax_unit("income_tax", period)
        return max_(income_tax, 0)
