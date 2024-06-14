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
        young_dependent = dependent & (age<p.age_threshold) 
        young_dependent_count = tax_unit.sum(young_dependent)
        dependent_count = tax_unit.sum(dependent)
        capped_dependent_count = min_(p.dependent_cap,dependent_count)
        rebate = p.amount.calc(age) * dependent  
        total_amount = tax_unit.sum(rebate)
        capped_amount = min_(total_amount,p.cap)
        return where(young_dependent_count>=p.dependent_cap,capped_amount,
              young_dependent_count*p.amount.calc(p.age_threshold-1) + (capped_dependent_count-young_dependent_count)*p.amount.calc(p.age_threshold+1))