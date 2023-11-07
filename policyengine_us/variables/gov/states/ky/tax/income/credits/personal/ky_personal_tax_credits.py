from policyengine_us.model_api import *


class ky_personal_tax_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky personal tax credits"
    unit = USD
    documentation = (
        "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=53500"
    )
    definition_period = YEAR
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.states.ky.tax.income.credits.personal

        blind_eligible_person = person(
            "ky_personal_tax_credits_blind_eligible", period
        )
        aged_eligible_person = person(
            "ky_personal_tax_credits_aged_eligible", period
        )

        military_eligible_person = person(
            "ky_personal_tax_credits_military_eligible", period
        )

        eligible_blind_people = p.amount.blind * blind_eligible_person 
        total_blind_people = tax_unit.sum(eligible_blind_people)

        eligible_aged_people = p.amount.aged * aged_eligible_person
        total_aged_people = tax_unit.sum(eligible_aged_people)

        eligible_military_people = p.amount.military * military_eligible_person
        total_military_people = tax_unit.sum(eligible_military_people)

        return total_blind_people + total_aged_people + total_military_people
