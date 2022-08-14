from openfisca_us.model_api import *


class in_base_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN base exemptions"
    unit = USD
    definition_period = YEAR
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-1-3.5"  # (a)(3)-(4)
    defined_for = StateCode.IN

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states["in"].tax.income.exemptions
        return tax_unit("tax_unit_size", period) * p.base.amount
