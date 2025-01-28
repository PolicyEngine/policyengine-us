from policyengine_us.model_api import *


class ct_personal_credit(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = "Connecticut personal credit"
    definition_period = YEAR
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):
        tax = tax_unit("ct_income_tax_before_personal_credit", period)
        rate = tax_unit("ct_personal_credit_rate", period)
        return tax * rate
