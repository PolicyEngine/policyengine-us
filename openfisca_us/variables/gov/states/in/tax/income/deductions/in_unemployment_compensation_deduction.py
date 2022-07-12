from gov.irs.income.taxable_income.adjusted_gross_income.adjusted_gross_income import (
    adjusted_gross_income,
)


from openfisca_us.model_api import *


class in_unemployment_compensation_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN Unemployment compensation deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-2-10"
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states["in"].tax.income.deductions
        unemployment_compensation_in_federal_AGI = tax_unit(
            "tax_unit_taxable_unemployment_compensation", period
        )
        federal_AGI = tax_unit("adjusted_gross_income", period)
        AGI_reduction = p.unemployment_compensation.agi_reduction[
            filing_status
        ]
        reduced_AGI = max(0, federal_AGI - AGI_reduction)
        in_taxable_unemployment_compensation = min(
            (0.5 * reduced_AGI), unemployment_compensation_in_federal_AGI
        )
        return (
            unemployment_compensation_in_federal_AGI
            - in_taxable_unemployment_compensation
        )
