from policyengine_us.model_api import *


class id_aged_or_disabled_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho aged or disabled credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        # The program includes individuals in the household, including those not in the filing unit.
        # We simplify by limiting to those in the filing unit.
        person = tax_unit.members
        p = parameters(
            period
        ).gov.states.id.tax.income.credits.aged_or_disabled
        eligible_person = person(
            "id_aged_or_disabled_credit_eligible_person", period
        )
        total_eligible_people = tax_unit.sum(eligible_person)
        capped_eligible_people = min_(total_eligible_people, p.person_cap)
        credit_amount = capped_eligible_people * p.amount
        # Filers cannot claim the credit if they claim the subtraction.
        # This variable verifies that.
        eligible = tax_unit("id_receives_aged_or_disabled_credit", period)
        return eligible * credit_amount
