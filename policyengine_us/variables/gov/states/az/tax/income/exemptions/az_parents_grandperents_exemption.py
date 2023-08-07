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
        cohabitating_parents = tax_unit("cohabitating_parents",period).astype(int)


        grandparents = tax_unit("tax_unit_grandparents", period)
        cohabitating_grand = tax_unit("cohabitating_grandparents",period).astype(int)

        payment_eligible = tax_unit("care_and_support_payment", period) > tax_unit("care_and_support_costs", period) * p.cost_rate
        eligibility = payment_eligible.astype(int)

        return (parents * cohabitating_parents + grandparents * cohabitating_grand) * eligibility * p.amount.parents_grandparents
