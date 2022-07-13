from openfisca_us.model_api import *


class in_person_military_service_deduction(Variable):
    value_type = float
    entity = Person
    label = "Person-level military service deduction for IN"
    definition_period = YEAR
    unit = USD
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-2-4"  # (a)(1)

    def formula(person, period, parameters):
        cap = (
            parameters(period)
            .gov.states["in"]
            .tax.income.deductions.military_service.max
        )
        return min_(person("military_service_income", period), cap)
