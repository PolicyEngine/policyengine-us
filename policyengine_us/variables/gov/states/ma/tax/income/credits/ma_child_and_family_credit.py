from policyengine_us.model_api import *


class ma_child_and_family_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Massachusetts child and family tax credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.mass.gov/info-details/massachusetts-child-and-family-tax-credit"
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ma.tax.income.credits.child_and_family
        person = tax_unit.members
        dependent = person("is_tax_unit_dependent", period)
        age = person("age", period)
        child = age < p.child_age_limit
        elderly = age >= p.elderly_age_limit
        disabled = person("is_disabled", period)
        eligible = dependent & (child | elderly | disabled)
        count_eligible = tax_unit.sum(eligible)
        capped_eligible = min_(count_eligible, p.dependent_cap)
        return capped_eligible * p.amount
