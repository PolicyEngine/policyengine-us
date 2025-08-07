from policyengine_us.model_api import *


class ne_military_retirement_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Nebraska military retirement subtraction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NE

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ne.tax.income.agi.subtractions.military_retirement
        person = tax_unit.members
        age = person("age", period)
        age_eligible = age >= p.age_threshold
        military_retirement_benefit = person("military_retirement_pay", period)
        qualifying_military_retirement_benefits = tax_unit.sum(
            military_retirement_benefit * age_eligible
        )
        # From 2015 to 2021, the tax filer may elect to exclude 40% of the military retirement benefit income for 7 consecutive years or elect to receive 15% exclusion for all tax years after age 67.
        return qualifying_military_retirement_benefits * p.fraction
