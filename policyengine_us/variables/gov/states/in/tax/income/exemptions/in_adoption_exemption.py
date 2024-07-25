from policyengine_us.model_api import *


class in_adoption_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana adoption exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/indiana/title-6/article-3/chapter-1/section-6-3-1-3-5/"  # (a)(5)(D)
    defined_for = StateCode.IN

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states["in"].tax.income.exemptions.adoption
        person = tax_unit.members
        is_qualifying_dependent_child = person(
            "in_is_qualifying_dependent_child", period
        )
        is_qualifying_adopted_dependent_child = (
            is_qualifying_dependent_child & person("is_adopted", period)
        )
        adopted_exemption_amount = p.amount
        return tax_unit.sum(
            is_qualifying_adopted_dependent_child * adopted_exemption_amount
        )
