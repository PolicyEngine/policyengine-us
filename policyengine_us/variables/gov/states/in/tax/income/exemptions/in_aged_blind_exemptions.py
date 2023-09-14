from policyengine_us.model_api import *


class in_aged_blind_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana exemptions for aged and or blind"
    unit = USD
    definition_period = YEAR
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-1-3.5"  # (a)(4)(B)
    defined_for = StateCode.IN

    def formula(tax_unit, period, parameters):
        aged_blind_count = tax_unit("aged_blind_count", period)
        p = parameters(period).gov.states["in"].tax.income.exemptions
        aged_blind_exemption = p.aged_blind.amount
        return aged_blind_count * aged_blind_exemption
