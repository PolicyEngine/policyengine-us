from policyengine_us.model_api import *


class mi_alternate_heating_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Alternate credit can be claimed"
    definition_period = YEAR
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        return ~tax_unit("heating_costs_included_in_rent", period)
