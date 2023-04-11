from policyengine_us.model_api import *


class ok_use_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oklahoma use tax"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdf"
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf"
    )
    defined_for = StateCode.OK

    def formula(tax_unit, period, parameters):
        fagi = tax_unit("adjusted_gross_income", period)
        p = parameters(period).gov.states.ok.tax
        return fagi * p.use.rate
