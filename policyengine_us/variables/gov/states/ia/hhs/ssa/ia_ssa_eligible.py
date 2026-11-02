from policyengine_us.model_api import *


class ia_ssa_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Iowa SSA non-income eligibility"
    definition_period = MONTH
    defined_for = StateCode.IA
    reference = (
        # Iowa Code 249.3
        "https://www.legis.iowa.gov/docs/code/249.pdf#page=2",
        # PDF pages 6-12
        "https://hhs.iowa.gov/media/3987/download?inline=#page=6",
        "https://www.ecfr.gov/current/title-20/section-416.1202",
        "https://www.ecfr.gov/current/title-20/section-416.1205",
    )

    def formula(person, period, parameters):
        category = person("ia_ssa_category", period)
        c = category.possible_values
        resource = person("ssi_countable_resources", period.this_year)
        community = (
            (category == c.IN_HOME_CARE)
            | (category == c.SMME)
            | (category == c.REGULAR)
            | (category == c.DEPENDENT_PERSON)
            | (category == c.FAMILY_LIFE_HOME)
        )
        # 6-B Resources p.12: "When the applicant is living with a spouse,
        # count the spouse's resources. When the applicant is not living with
        # the spouse, do not count the spouse's resources." A residential care
        # resident lives apart from the spouse after the month of entry (6-B
        # p.60), so only the couple-budget entry month pools resources
        # (ia_ssa.yaml Case 61).
        # NOTE: The spouse who stays at home still pools resources with the
        # resident after the month of entry, though p.12 would test that
        # spouse alone. Federal SSI in the model has no input for spouses who
        # live apart and keeps them a couple, and that spouse's SSA income
        # comes from federal SSI, so this belongs with the federal treatment of
        # spouses living apart.
        couple = person("ia_ssa_has_spouse", period) & (
            community | person("ia_ssa_rcf_couple_budget", period)
        )
        resource = where(couple, person.marital_unit.sum(resource), resource)
        resource = resource + person("ia_ssa_resources_deemed_from_parents", period)
        # 6-B Resources prints "$2,000 for an individual" and "$3,000 for a
        # married couple living together" under 20 CFR 416.1202; these equal
        # the SSI limits of 20 CFR 416.1205, so the federal parameters are used
        # and an SSI reform carries over to Iowa.
        limit = parameters(period).gov.ssa.ssi.eligibility.resources.limit
        return person("ia_ssa_nonfinancial_eligible", period) & (
            resource <= where(couple, limit.couple, limit.individual)
        )
