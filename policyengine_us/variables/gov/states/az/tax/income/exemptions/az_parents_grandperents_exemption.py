from policyengine_us.model_api import *


class az_parents_grandparents_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona parents and grandparents exemption"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.az.tax.income.exemptions
        parents = tax_unit("tax_unit_parent", period)
        grandparents = tax_unit("tax_unit_grandparent", period)
        
        return (parents + grandparents) * p.parents_grandparents
