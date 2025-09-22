from policyengine_us.model_api import *


class ok_income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oklahoma income tax before credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdf"
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf"
    )
    defined_for = StateCode.OK

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        taxable_income = tax_unit("ok_taxable_income", period)
        p = parameters(period).gov.states.ok.tax.income.rates

        return select_filing_status_value(filing_status, p, taxable_income)
