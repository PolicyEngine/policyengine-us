from policyengine_us.model_api import *


class ia_ssa_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Iowa SSA non-income eligibility"
    definition_period = MONTH
    reference = ("https://hhs.iowa.gov/media/3987/download?inline=",)
    defined_for = StateCode.IA

    def formula(person, period, parameters):
        category = person("ia_ssa_category", period)
        c = category.possible_values
        resource = person("ssi_countable_resources", period.this_year)
        joint = person("ssi_claim_is_joint", period.this_year)
        community = (
            (category == c.IN_HOME_CARE)
            | (category == c.SMME)
            | (category == c.REGULAR)
            | (category == c.DEPENDENT_PERSON)
            | (category == c.FAMILY_LIFE_HOME)
        )
        couple = (person.marital_unit.nb_persons() == 2) & (community | joint)
        resource = where(couple, person.marital_unit.sum(resource), resource)
        resource = resource + person("ia_ssa_resources_deemed_from_parents", period)
        p = parameters(period).gov.ssa.ssi.eligibility.resources.limit
        immigration = person("immigration_status", period.this_year)
        citizen = immigration == immigration.possible_values.CITIZEN
        immigrant = person("is_ssi_qualified_noncitizen", period.this_year)
        return (
            person("is_ssi_aged_blind_disabled", period.this_year)
            & (citizen | immigrant)
            & (resource <= where(couple, p.couple, p.individual))
            & (category != c.NONE)
            & ~person("is_incarcerated", period)
            & person("takes_up_ssi_if_eligible", period)
        )
