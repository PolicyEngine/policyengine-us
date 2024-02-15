from policyengine_us.model_api import *


class num(Variable):
    value_type = int
    entity = TaxUnit
    label = "Numeric value whether the filing status is married filing jointly"
    definition_period = YEAR
    documentation = (
        "2 when filing_status is married filing jointly; otherwise 1"
    )
    unit = USD

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        return where(
            filing_status == filing_status.possible_values.JOINT, 2, 1
        )
