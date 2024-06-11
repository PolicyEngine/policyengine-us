from policyengine_us.model_api import *


class az_income_tax_rebates(Variable):
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
        below_age_threshold = person("age", period) < p.age_threshold
        above_age_threshold = person("age", period) > p.age_threshold
        younger_dependent = below_age_threshold & person(
            "is_tax_unit_dependent", period
        )
        older_dependent = above_age_threshold & person(
            "is_tax_unit_dependent", period
        )
        younger_dependent_number = tax_unit.sum(younger_dependent)
        older_dependent_number = tax_unit.sum(older_dependent)
        total_dependent_number = (
            younger_dependent_number + older_dependent_number
        )
        if younger_dependent_number > p.cap_quantity:
            return p.cap_amount
        elif total_dependent_number > p.cap_quantity:
            return (
                p.younger_amount * younger_dependent_number
                + p.older_amount * (p.cap_quantity - younger_dependent_number)
            )
        else:
            return (
                p.younger_amount * younger_dependent_number
                + p.older_amount * older_dependent_number
            )
