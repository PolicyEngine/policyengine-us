from openfisca_us.model_api import *


class maximum_capital_loss(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maximum capital loss deduction"
    unit = USD
    documentation = "The capital loss deductible from gross income."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/1211"

    def formula(tax_unit, period, parameters):
        capital_loss = tax_unit("tax_unit_capital_loss", period)
        filing_status = tax_unit("filing_status", period)
        max_loss = parameters(period).irs.ald.loss.capital.max[filing_status]
        return min_(max_loss, capital_loss)
