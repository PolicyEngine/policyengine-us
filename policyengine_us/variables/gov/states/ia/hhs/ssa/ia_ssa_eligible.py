from policyengine_us.model_api import *


class ia_ssa_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Iowa SSA non-income eligibility"
    definition_period = MONTH
    defined_for = StateCode.IA
    reference = (
        # Iowa Code 249.3
        "https://www.legis.iowa.gov/docs/code/249.pdf#page=1",
        # PDF pages 6-12
        "https://hhs.iowa.gov/media/3987/download?inline=#page=6",
        "https://www.ecfr.gov/current/title-20/section-416.1202",
    )

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
        # 6-B Resources: "When the applicant is living with a spouse, count the
        # spouse's resources."
        couple = (person.marital_unit.nb_persons() == 2) & (community | joint)
        resource = where(couple, person.marital_unit.sum(resource), resource)
        resource = resource + person("ia_ssa_resources_deemed_from_parents", period)
        # 6-B Resources prints "$2,000 for an individual" and "$3,000 for a
        # married couple living together" under 20 CFR 416.1202; these equal
        # the SSI limits, so the federal parameters are used and an SSI reform
        # carries over to Iowa.
        limit = parameters(period).gov.ssa.ssi.eligibility.resources.limit
        return person("ia_ssa_nonfinancial_eligible", period) & (
            resource <= where(couple, limit.couple, limit.individual)
        )
