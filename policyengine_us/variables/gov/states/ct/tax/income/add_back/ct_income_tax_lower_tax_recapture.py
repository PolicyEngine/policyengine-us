from policyengine_us.model_api import *


class ct_income_tax_lower_tax_recapture(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut income tax lower tax recapture"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):