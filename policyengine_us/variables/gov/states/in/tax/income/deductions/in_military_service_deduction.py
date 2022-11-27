from policyengine_us.model_api import *


class in_military_service_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN military service deduction"
    definition_period = YEAR
    unit = USD
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-2-4"  # (a)(1)

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = (
            parameters(period)
            .gov.states["in"]
            .tax.income.deductions.military_service
        )
        person_deduction = min_(
            person("military_service_income", period), p.max
        )
        return tax_unit.sum(person_deduction)
