from policyengine_us.model_api import *


class me_property_tax_fairness_credit_veterans_cap(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = "Veterans cap for Maine property tax fairness credit"
    definition_period = YEAR
    defined_for = StateCode.ME

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.me.tax.income.credits.fairness.property_tax
        base_cap = tax_unit("me_property_tax_fairness_credit_base_cap", period)
        return base_cap * p.veterans_matched
