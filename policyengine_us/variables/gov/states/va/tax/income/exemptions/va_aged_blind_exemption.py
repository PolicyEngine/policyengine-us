from policyengine_us.model_api import *


class va_aged_blind_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia aged/blind exemption"
    defined_for = StateCode.VA
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.va.tax.income.exemptions
        aged_blind_count = tax_unit("aged_blind_count", period)
        return aged_blind_count * p.aged_blind
