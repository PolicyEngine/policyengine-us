from policyengine_us.model_api import *


class ky_personal_tax_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky personal tax credits"
    unit = USD
    documentation = "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=53500"
    definition_period = YEAR
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(
            period
        ).gov.states.ky.tax.income.credits.personal

        eligible_person = person(
            "ky_personal_tax_credits_eligible", period
        )

        blind_amt = p.amount.blind
        eligible_blind_amt = blind_amt * eligible_person
        total_blind_amt = tax_unit.sum(eligible_blind_amt)

        aged_amt = p.amount.aged
        eligible_aged_amt = aged_amt * eligible_person
        total_aged_amt = tax_unit.sum(eligible_aged_amt)

        total_personal_amt = total_blind_amt + total_aged_amt

        return total_personal_amt
