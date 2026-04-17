from policyengine_us.model_api import *


class ok_529_plan_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oklahoma deduction for contributions to 529 plans"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.oklahoma529.com/resources/faq/",
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf#page=16",
    )
    defined_for = StateCode.OK

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ok.tax.income.agi.subtractions.plan_529
        contributions = tax_unit("investment_in_529_plan", period)
        filing_status = tax_unit("filing_status", period)
        cap = p.cap[filing_status]
        return min_(contributions, cap)
