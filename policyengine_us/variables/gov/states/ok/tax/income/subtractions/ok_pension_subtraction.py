from policyengine_us.model_api import *


class ok_pension_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oklahoma pension subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdf"
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf"
    )
    defined_for = StateCode.OK

    def formula(tax_unit, period, parameters):
        pensions = tax_unit.members("taxable_pension_income", period)
        p = parameters(period).gov.states.ok.tax.income.agi.subtractions
        return tax_unit.sum(min_(p.pension_limit, pensions))
