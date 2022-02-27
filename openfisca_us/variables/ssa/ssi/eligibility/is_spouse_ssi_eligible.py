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
        eligible_family_members = family.members("is_ssi_eligible", period)
        # Each family should have at most two married people.
        married_eligible_family_members = family.sum(
            married_family_members & eligible_family_members
        )
        self_married_eligible = and_(
            person, period, ["is_ssi_eligible", "is_married"]
        )
        return self_married_eligible & (married_eligible_family_members > 1)
