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
        person = tax_unit.members
        # The exemption is provided for parents and grandparents who receive over 50% of their care and support
        # payments from teh filer
        care_and_support_payment = person("care_and_support_payment", period)
        care_and_support_costs = person("care_and_support_costs", period)
        support_payment_ratio = np.zeros_like(care_and_support_costs)
        mask = care_and_support_costs != 0
        support_payment_ratio[mask] = care_and_support_payment[mask] / care_and_support_costs[mask]
        payment_eligibility = support_payment_ratio > 0
        # Eligible parents of ancestors of parents have to be at or over 65 as well as cohabiting with the filer
        age = person("age", period)
        age_eligible = age >= p.parent_grandparent.min_age

        cohabitating_parent = person("cohabitating_parent", period)
        eligible_co_age_p = cohabitating_parent & age_eligible
        eligible_parent = payment_eligibility & cohabitating_parent & age_eligible

        cohabitating_grandparent = person("cohabitating_grandparent", period)
        eligible_co_age_g = cohabitating_grandparent & age_eligible
        eligible_grandparent = eligible_co_age_g & payment_eligiblity

        total_exemptions = eligible_parent + eligible_grandparent
        return p.parent_grandparent.amount * tax_unit.sum(total_exemptions)
