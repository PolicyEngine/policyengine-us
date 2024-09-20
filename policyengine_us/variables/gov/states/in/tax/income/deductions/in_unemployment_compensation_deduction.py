from policyengine_us.model_api import *


class in_unemployment_compensation_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana unemployment compensation deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-2-10"
    )
    defined_for = StateCode.IN

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states["in"].tax.income.deductions
        unemployment_compensation_in_federal_agi = tax_unit(
            "tax_unit_taxable_unemployment_compensation", period
        )
        federal_agi = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        agi_reduction = p.unemployment_compensation.agi_reduction[
            filing_status
        ]
        reduced_agi = max_(0, federal_agi - agi_reduction)
        reduced_agi_haircut = p.unemployment_compensation.reduced_agi_haircut
        in_taxable_unemployment_compensation = min_(
            (reduced_agi_haircut * reduced_agi),
            unemployment_compensation_in_federal_agi,
        )
        return (
            unemployment_compensation_in_federal_agi
            - in_taxable_unemployment_compensation
        )
