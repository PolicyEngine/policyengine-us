from policyengine_us.model_api import *


class az_one_time_families_tax_rebates(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona one-time families tax rebates"
    unit = USD
    definition_period = YEAR
    defined_for = "az_income_tax_rebates_eligibility"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.az.tax.income.rebates
        person = tax_unit.members
        dependent = person("is_tax_unit_dependent", period)
        age = person("age", period)
        dependent_count = tax_unit.sum(dependent)
        capped_dependent_count = min_(p.dependent_cap,tax_unit.sum(dependent))
        rebate = p.amount.calc(age) * dependent  
        total_amount = tax_unit.sum(rebate)
        return min_(total_amount,p.cap)