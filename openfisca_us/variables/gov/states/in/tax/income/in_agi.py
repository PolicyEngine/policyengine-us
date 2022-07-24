from openfisca_us.model_api import *


class in_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-1-3.5"
    )
    defined_for = StateCode.IN

    def formula(tax_unit, period, parameters):
        federal_agi = tax_unit("adjusted_gross_income", period)
        in_add_backs = tax_unit("in_add_backs", period)
        in_deductions = tax_unit("in_deductions", period)
        in_exemptions = tax_unit("in_exemptions", period)

        return federal_agi + in_add_backs - in_deductions - in_exemptions
