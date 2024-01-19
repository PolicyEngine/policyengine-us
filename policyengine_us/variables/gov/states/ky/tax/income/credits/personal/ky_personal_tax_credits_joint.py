from policyengine_us.model_api import *


class ky_personal_tax_credits_person(Variable):
    value_type = float
    entity = Person
    label = "Kentucky personal tax credits for each person"
    unit = USD
    reference = "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=53500#page=3"  # (3) (a)
    definition_period = YEAR
    defined_for = StateCode.KY


    def formula(person, period, parameters):
        is_head = person("is_tax_unit_head", period)
        blind_personal_tax_credits = person(
            "ky_blind_personal_tax_credits", period
        )
        aged_personal_tax_credits = person(
            "ky_aged_personal_tax_credits", period
        )
        military_personal_tax_credits = person(
            "ky_military_personal_tax_credits", period
        )
        head_blind_personal_tax_credits = is_head * person.tax_unit.sum(
            blind_personal_tax_credits
        )
        head_aged_personal_tax_credits = is_head * person.tax_unit.sum(
            aged_personal_tax_credits
        )
        head_military_personal_tax_credits = is_head * person.tax_unit.sum(
            military_personal_tax_credits
        )

        return (
            head_blind_personal_tax_credits
            + head_aged_personal_tax_credits
            + head_military_personal_tax_credits
        )
