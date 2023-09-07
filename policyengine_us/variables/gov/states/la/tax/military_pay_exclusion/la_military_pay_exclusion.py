from policyengine_us.model_api import *


class la_military_pay_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana military pay exclusion"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.LA

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.la.tax.military_pay_exclusion
        compensation = tax_unit(
            "la_military_compensation", period
        )
        max_amount=p.max_amount
        amount=compensation > max_amount
        return where(amount,max_amount, compensation)
