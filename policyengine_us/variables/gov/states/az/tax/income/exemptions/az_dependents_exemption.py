from policyengine_us.model_api import *


class az_dependents_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona dependents credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        dep_under17 = tax_unit("dependents_under17", period)
        dep_over17 = tax_unit("dependents_over17", period)

        p = parameters(period).gov.states.az.tax.income.exemptions

        return dep_over17 * p.dependents_over17 + dep_under17 * p.dependents_undr17
