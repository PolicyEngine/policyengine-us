from policyengine_us.model_api import *


class limited_capital_loss(Variable):
    value_type = float
    entity = TaxUnit
    label = "Limited capital loss deduction"
    unit = USD
    documentation = "The capital loss deductible from gross income."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/1211"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs
        filing_status = tax_unit("filing_status", period)
        max_loss = p.ald.loss.capital.max[filing_status]
        # A tax-unit dependent's capital losses belong on the dependent's own
        # return, as in irs_gross_income.
        capital_losses = tax_unit_non_dep_sum("capital_losses", tax_unit, period)
        return min_(max_loss, capital_losses)
