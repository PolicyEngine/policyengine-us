from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed.ssi_resources_deemed_from_ineligible_parent import (
    _ssi_parental_resource_pool,
)
from policyengine_us.variables.household.demographic.person._parent_links import (
    has_parent_ids,
    unlinked_parent,
)


class is_optional_senior_or_disabled_asset_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Asset-eligibility for State’s optional Medicaid pathway for seniors or people with disabilities"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396a#m",
        "https://www.law.cornell.edu/uscode/text/42/1396d#p",
        "https://revisor.mo.gov/main/OneSection.aspx?section=208.010",
        "https://www.law.cornell.edu/regulations/california/22-CCR-50420",
        "https://dssmanuals.mo.gov/mo-healthnet-for-the-aged-blind-and-disabled/0805-000-00/0805-020-00/0805-020-05/",
        "https://dssmanuals.mo.gov/mo-healthnet-for-the-aged-blind-and-disabled/0805-000-00/0805-020-00/0805-020-10/",
        "https://dssmanuals.mo.gov/wp-content/uploads/2018/10/appendix_k.pdf#page=2",
    )

    def formula(person, period, parameters):
        #  Assets
        # SSI financial responsibility rules (42 CFR 435.602): the unit is
        # the individual or the married couple, not the tax filing unit.
        personal_assets = person("ssi_countable_resources", period)  # $
        is_couple = person.marital_unit.nb_persons() == 2
        state = person.household("state_code_str", period)

        #  Parameters
        p = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.senior_or_disabled

        # Missouri deems "the entire amount" of the available resources of a
        # parent a child lives with, leaving out retirement accounts, which
        # ssi_countable_resources does not count, and "resources owned solely
        # by the stepparent" (MHABD 0805.020.10). The SSI pool also holds a
        # parent's spouse, so count only parents. A child who is married, or in
        # a facility or foster care, does not live with a parent (MHABD
        # 0805.020.05).
        # NOTE: The exception for a parent or parent's spouse on non-spend-down
        # Medicaid is not modeled, because the parent's Medicaid eligibility
        # depends on this variable. Parent ids may name a stepparent, and a
        # stepparent with children of their own is a parent here. Resources
        # held jointly with a stepparent count only if entered on the parent.
        month = period.first_month
        resources = person("ssi_resources_for_deeming", month)
        is_parent = person("is_parent", month)
        parent_resources, _, _ = _ssi_parental_resource_pool(
            person, month, resources * is_parent
        )
        parents, _, _ = _ssi_parental_resource_pool(person, month, is_parent)
        # Without parent ids, a minor parent's pool holds their own row. Their
        # resources are already the child's own, and they are not their own
        # parent.
        own_row = unlinked_parent(person, month) & ~has_parent_ids(person, month)
        parental_resources = parent_resources - own_row * resources
        parent_count = parents - own_row
        deems_parents = (
            p.assets.deems_entire_parental_resources[state].astype(bool)
            & person("is_ssi_aged_blind_disabled", period)
            & person("is_child", period)
            & (person.marital_unit.nb_persons() == 1)
            & ~person("ssi_lives_in_medical_treatment_facility", month)
            & ~person("is_in_foster_care", month)
        )
        # Inputs are stored as float32, so compare whole cents with the limit.
        assets = np.round(
            person.marital_unit.sum(personal_assets)
            + where(deems_parents, parental_resources, 0),
            2,
        )

        # Maine excludes savings up to a set amount (22 M.R.S. § 3174-AA(2)).
        # Its savings include bank accounts, stocks and bonds, which make up
        # all of the SSI countable resources modeled here.
        me = parameters(period).gov.states.me.dhhs.medicaid.savings_exclusion
        me_exclusion = where(is_couple, me.couple, me.individual)
        savings_exclusion = where(state == "ME", me_exclusion, 0)
        assets = max_(assets - savings_exclusion, 0)

        #  Asset limit
        # Missouri's Appendix K sets the same amounts for a "Child living with
        # 1 parent" and a "Child living with 2 parents" as for an individual
        # and a couple.
        uses_couple_limit = is_couple | (deems_parents & (parent_count > 1))
        state_limit = where(
            uses_couple_limit,
            p.assets.limit.couple[state],
            p.assets.limit.individual[state],
        )
        # Flagged states use the QMB / Medicare Savings Program resource
        # standard instead of a state dollar limit.
        msp = parameters(period).gov.hhs.medicare.savings_programs.eligibility.asset
        msp_limit = where(is_couple, msp.couple, msp.individual)
        uses_msp_limit = p.assets.limit.uses_msp_limit[state].astype(bool)

        # The MSP resource standard (42 USC 1396d(p)(1)(C)) and the AR, OK
        # and SC rules allow resources equal to the limit.
        within_msp_limit = assets <= msp_limit
        # RSMo 208.010.2(7): a Missouri claimant "owns or possesses resources
        # not to exceed" the individual amount, and a married couple "may own
        # resources not to exceed" the couple amount. California resources may
        # not exceed the limit (22 CCR 50420(a); WIC 14005.40(c)(5)).
        inclusive = where(
            uses_couple_limit,
            p.assets.limit.couple_limit_inclusive[state],
            p.assets.limit.individual_limit_inclusive[state],
        ).astype(bool)
        within_state_limit = where(
            inclusive, assets <= state_limit, assets < state_limit
        )
        return where(uses_msp_limit, within_msp_limit, within_state_limit)
