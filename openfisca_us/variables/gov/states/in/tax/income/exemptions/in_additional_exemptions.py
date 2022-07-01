from openfisca_us.model_api import *


class in_additional_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN additional exemptions"
    unit = USD
    definition_period = YEAR
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-1-3.5"  # (a)(4)(A)

    def formula(tax_unit, period, parameters):
        additional_exemptions_count = tax_unit(
            "in_qualifying_child_count", period
        )
        p = parameters(period).gov.states["in"].tax.income.exemptions
        additional_exemption = p.additional.amount
        return additional_exemptions_count * additional_exemption
