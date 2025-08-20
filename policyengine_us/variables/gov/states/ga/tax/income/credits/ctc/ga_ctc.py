from policyengine_us.model_api import *


class ga_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia Child Tax Credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.GA
    reference = (
        "https://legiscan.com/GA/text/HB136/id/3204611/Georgia-2025-HB136-Enrolled.pdf#page=2",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ga.tax.income.credits.ctc
        person = tax_unit.members
        age = person("age", period)
        ctc_eligible_child = person("ctc_qualifying_child", period)
        ga_child_age_eligible = age < p.age_threshold
        eligible_children = tax_unit.sum(ctc_eligible_child & ga_child_age_eligible)

        base_amount = eligible_children * p.amount
        tax_before_nonref = tax_unit(
            "ga_income_tax_before_non_refundable_credits", period
        )

        return min_(base_amount, tax_before_nonref)


