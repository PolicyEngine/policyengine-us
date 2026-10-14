from policyengine_us.model_api import *


class in_military_retirement_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana military retirement deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-2-4",
        "https://forms.in.gov/Download.aspx?id=16915#page=20",
    )
    defined_for = StateCode.IN

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = (
            parameters(period)
            .gov.states["in"]
            .tax.income.deductions.military_retirement
        )
        military_retirement = person("military_retirement_pay", period) + person(
            "military_retirement_pay_survivors", period
        )
        excess = max_(0, military_retirement - p.base)
        person_deduction = min_(military_retirement, p.base) + p.excess_rate * excess
        return tax_unit.sum(person_deduction)
