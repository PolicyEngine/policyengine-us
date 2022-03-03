from openfisca_us.model_api import *


class is_spouse_ssi_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    documentation = "Spouse's eligibility for Supplemental Security Income"
    label = "Spouse's SSI eligibility"

    def formula(person, period, parameters):
        # Spouse is eligible if there is another married eligible person in
        # the family.
        family = person.family
        married_family_members = family.members("is_married", period)
        abd_family_members = family.members(
            "is_ssi_aged_blind_disabled", period
        )
        # Each family should have at most two married people.
        married_abd_family_members = family.sum(
            married_family_members & abd_family_members
        )
        self_married_abd = and_(
            person, period, ["is_ssi_aged_blind_disabled", "is_married"]
        )
        return self_married_abd & (married_abd_family_members > 1)
