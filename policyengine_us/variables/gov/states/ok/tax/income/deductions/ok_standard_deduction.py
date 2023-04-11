from policyengine_us.model_api import *


class ok_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oklahoma standard deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdf"
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf"
    )
    defined_for = StateCode.OK

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ok.tax.income
        filing_status = tax_unit("filing_status", period)
        return p.deductions.standard.amount[filing_status]
