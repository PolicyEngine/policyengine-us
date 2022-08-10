from openfisca_us.model_api import *


class ny_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY standard deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/613"
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        dependent_elsewhere = tax_unit("tax_unit_dependent_elsewhere", period)
        standard_deduction = parameters(
            period
        ).gov.states.ny.tax.income.deductions.standard
        filing_status = tax_unit("filing_status", period)
        return where(
            dependent_elsewhere,
            standard_deduction.dependent_elsewhere,
            standard_deduction.amount[filing_status],
        )
