from policyengine_us.model_api import *


class nj_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        return add(
            tax_unit,
            period,
            ["nj_property_tax_credit", "nj_eitc", "nj_ctc"],
        )

    def formula_2021(tax_unit, period, parameters):
        return add(
            tax_unit,
            period,
            ["nj_property_tax_credit", "nj_eitc", "nj_cdcc", "nj_ctc"],
        )
