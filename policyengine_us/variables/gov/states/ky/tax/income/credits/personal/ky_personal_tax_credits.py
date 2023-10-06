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

        blind_amt = p.amount.blind
        eligible_blind_amt = blind_amt * blind_eligible_person
        total_blind_amt = tax_unit.sum(eligible_blind_amt)

        aged_amt = p.amount.aged
        eligible_aged_amt = aged_amt * aged_eligible_person
        total_aged_amt = tax_unit.sum(eligible_aged_amt)

        military_amt = p.amount.military
        eligible_military_amt = military_amt * military_eligible_person
        total_military_amt = tax_unit.sum(eligible_military_amt)

        return total_blind_amt + total_aged_amt + total_military_amt
