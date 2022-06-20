from openfisca_us.model_api import *


class loss_ald(Variable):
    value_type = float
    entity = TaxUnit
    label = "Business loss ALD"
    unit = USD
    documentation = (
        "Above-the-line deduction from gross income for business losses."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/165"

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        max_loss = parameters(period).gov.irs.ald.loss.max[filing_status]
        personal_self_employment_loss = max_(
            -tax_unit.members("self_employment_income", period), 0
        )
        tax_unit_self_employment_losses = tax_unit.sum(
            personal_self_employment_loss
        )
        capital_loss = max_(tax_unit("maximum_capital_loss", period), 0)
        return min_(max_loss, tax_unit_self_employment_losses + capital_loss)
