from policyengine_us.model_api import *


class ga_surplus_tax_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia surplus tax rebate"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.legis.ga.gov/api/legislation/document/20232024/217823"
    )
    defined_for = StateCode.GA

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        p = parameters(
            period
        ).gov.states.ga.tax.income.credits.surplus_tax_rebate
        return p.amount[filing_status]
