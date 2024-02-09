from policyengine_us.model_api import *


class ky_personal_tax_credits_joint(Variable):
    value_type = float
    entity = Person
    label = "Kentucky personal tax credits when married couples file jointly"
    unit = USD
    reference = "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=53500#page=3"  # (3) (a)
    definition_period = YEAR
    defined_for = StateCode.KY

    def formula(person, period, parameters):
        ky_blind_personal_tax_credits = person(
            "ky_blind_personal_tax_credits", period
        )
        ky_aged_personal_tax_credits = person(
            "ky_aged_personal_tax_credits", period
        )
        ky_military_personal_tax_credits = person(
            "ky_military_personal_tax_credits", period
        )
        is_head = person("is_tax_unit_head", period)
        total_blind = person.tax_unit.sum(ky_blind_personal_tax_credits)
        total_aged = person.tax_unit.sum(ky_aged_personal_tax_credits)
        total_military = person.tax_unit.sum(ky_military_personal_tax_credits)

        return is_head * (total_blind + total_aged + total_military)
