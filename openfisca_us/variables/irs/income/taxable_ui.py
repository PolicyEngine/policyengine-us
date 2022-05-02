from openfisca_us.model_api import *


class taxable_ui(Variable):
    value_type = float
    entity = TaxUnit
    label = "Taxable unemployment insurance"
    unit = USD
    documentation = "Unemployment insurance included in AGI."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/85"

    def formula(tax_unit, period, parameters):
        ui = parameters(period).irs.unemployment_insurance
        ui_amount = tax_unit("tax_unit_ui", period)
        agi = tax_unit("adjusted_gross_income", period)
        agi_over_ui = agi - ui_amount
        filing_status = tax_unit("filing_status", period)
        ui_excluded = where(
            agi_over_ui <= ui.exemption.cutoff[filing_status],
            min_(ui_amount, ui.exemption.amount),
            0,
        )
        return ui_amount - ui_excluded
