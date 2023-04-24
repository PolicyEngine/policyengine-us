from policyengine_us.model_api import *


class ok_agi_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oklahoma AGI subtractions from federal AGI"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdf"
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf"
    )
    defined_for = StateCode.OK

    def formula(tax_unit, period, parameters):
        oasdi = add(tax_unit, period, ["taxable_social_security"])
        pensions = tax_unit.members("taxable_pension_income", period)
        p = parameters(period).gov.states.ok.tax.income.agi.subtractions
        capped_pension = tax_unit.sum(min_(p.pension_limit, pensions))
        return oasdi + capped_pension
