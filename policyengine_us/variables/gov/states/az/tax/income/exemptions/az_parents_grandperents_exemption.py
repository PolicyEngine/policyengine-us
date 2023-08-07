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

        parents = tax_unit("tax_unit_parents", period)
        if_cohabitating_parents = tax_unit("is_cohabitating_parents",period).astype(int)


        grandparents = tax_unit("tax_unit_grandparents", period)
        if_cohabitating_grand = tax_unit("is_cohabitating_grandparents",period).astype(int)
        
        cost = tax_unit("care_and_support_costs",period) >= tax_unit("")

        return (parents * cohabitating_parents + grandparents * cohabitating_grand) * p.amount.parents_grandparents
