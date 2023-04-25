from policyengine_us.model_api import *


class in_aged_low_agi_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN base exemptions"
    unit = USD
    definition_period = YEAR
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-1-3.5"  # (a)(5)(C)
    defined_for = StateCode.IN

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states["in"].tax.income.exemptions
        filing_status = tax_unit("filing_status", period)
        threshold = p.aged_low_agi.threshold[filing_status]
        aged_low_agi_exemption = p.aged_low_agi.amount
        federal_agi = tax_unit("adjusted_gross_income", period)
        aged_head = tax_unit("aged_head", period).astype(int)
        aged_spouse = tax_unit("aged_spouse", period).astype(int)
        income_eligible = where(
            federal_agi < threshold, 1, 0
        )  # The law specifies "Less than".
        return (
            income_eligible
            * (aged_head + aged_spouse)
            * aged_low_agi_exemption
        )
