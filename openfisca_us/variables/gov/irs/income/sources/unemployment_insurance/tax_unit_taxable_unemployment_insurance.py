from openfisca_us.model_api import *


class tax_unit_taxable_unemployment_compensation(Variable):
    value_type = float
    entity = TaxUnit
    label = "Taxable unemployment compensation"
    unit = USD
    documentation = "Unemployment compensation included in AGI."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/85"

    def formula(tax_unit, period, parameters):
        ui = parameters(period).irs.unemployment_compensation
        uc_amount = tax_unit("tax_unit_unemployment_compensation", period)
        agi = tax_unit("taxable_uc_agi", period)
        agi_over_uc = agi - uc_amount
        filing_status = tax_unit("filing_status", period)
        uc_excluded = where(
            agi_over_uc <= ui.exemption.cutoff[filing_status],
            min_(uc_amount, ui.exemption.amount),
            0,
        )
        return uc_amount - uc_excluded
