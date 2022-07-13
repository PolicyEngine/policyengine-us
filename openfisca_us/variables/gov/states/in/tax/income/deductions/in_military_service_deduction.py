from openfisca_us.model_api import *


class in_military_service_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN military service deduction"
    definition_period = YEAR
    unit = USD
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-2-4"  # (a)(1)

    def formula(tax_unit, period, parameters):
        deductions = tax_unit.members(
            "in_person_military_service_deduction", period
        )
        sum_deductions = tax_unit.sum(deductions)
        return sum_deductions
