from policyengine_us.model_api import *


class ks_income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kansas income tax before credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ksrevenue.gov/pdf/ip21.pdf"
        "https://www.ksrevenue.gov/pdf/ip22.pdf"
    )
    defined_for = StateCode.KS

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        taxable_income = tax_unit("ks_taxable_income", period)
        p = parameters(period).gov.states.ks.tax.income.rates
        tax = where(
            filing_status == filing_status.possible_values.JOINT,
            p.joint.calc(taxable_income),
            p.other.calc(taxable_income),
        )
        zero_tax_agi_threshold = p.zero_tax_threshold[filing_status]
        agi = tax_unit("ks_agi", period)
        return where(agi <= zero_tax_agi_threshold, 0, tax)
