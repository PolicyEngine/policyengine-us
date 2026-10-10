from policyengine_us.model_api import *


class is_ssi_spousal_resource_deeming_applies(Variable):
    value_type = bool
    entity = Person
    label = "Ineligible spouse's resources are deemed for SSI"
    definition_period = MONTH
    reference = (
        "https://www.ecfr.gov/current/title-20/section-416.1202#p-416.1202(a)",
        "https://secure.ssa.gov/poms.nsf/lnx/0501330100",
        "https://www.ecfr.gov/current/title-20/section-416.1167",
    )

    def formula(person, period, parameters):
        # Use the same tax-head/spouse convention as SSI income deeming and
        # ssi_claim_is_joint. A marital unit alone cannot establish marriage:
        # situations omitting marital units put everyone in one default unit.
        ineligible = person("is_ssi_ineligible_spouse", period)
        # Marital units represent spouses living together. Subtract self:
        # an unmarried ineligible adult is not their own ineligible spouse.
        has_ineligible_spouse = person.marital_unit.sum(ineligible) > ineligible
        households = person.household.reference_entity.members_entity_id
        first_home = person.marital_unit.value_nth_person(0, households, default=-1)
        second_home = person.marital_unit.value_nth_person(1, households, default=-2)
        # 416.1167 retains the absent person's household membership. Enter a
        # temporarily absent spouse in the household they remain a member of.
        return (
            person("is_ssi_aged_blind_disabled", period)
            & person("is_tax_unit_head_or_spouse", period)
            & ~person("ssi_claim_is_joint", period)
            & has_ineligible_spouse
            & (first_home == second_home)
        )
