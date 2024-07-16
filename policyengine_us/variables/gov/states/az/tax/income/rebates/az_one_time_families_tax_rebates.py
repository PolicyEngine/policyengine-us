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
        age = person("age", period) - 2  # the age at the end of 2021
        dependent = person("is_tax_unit_dependent", period) & (age > 0)
        young_dependent = dependent & (age < p.amount.thresholds[-1])
        young_dependent_count = tax_unit.sum(young_dependent)
        dependent_count = tax_unit.sum(dependent)
        capped_dependent_count = min_(p.dependent_cap, dependent_count)
        rebate = p.amount.calc(age) * dependent
        total_amount = tax_unit.sum(rebate)
        capped_amount = min_(total_amount, p.cap)
        young_amount = young_dependent_count * p.amount.calc(
            p.amount.thresholds[-1] - 1
        )
        old_amount = (
            capped_dependent_count - young_dependent_count
        ) * p.amount.calc(p.amount.thresholds[-1] + 1)
        return where(
            young_dependent_count >= p.dependent_cap,
            capped_amount,
            young_amount + old_amount,
        )
