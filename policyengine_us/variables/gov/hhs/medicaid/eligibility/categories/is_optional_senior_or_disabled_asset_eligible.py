from policyengine_us.model_api import *


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
    )

    def formula(person, period, parameters):
        #  Assets
        # SSI financial responsibility rules (42 CFR 435.602): the unit is
        # the individual or the married couple, not the tax filing unit.
        personal_assets = person("ssi_countable_resources", period)  # $
        # Inputs are stored as float32, so compare whole cents with the limit.
        assets = np.round(person.marital_unit.sum(personal_assets), 2)
        is_couple = person.marital_unit.nb_persons() == 2
        state = person.household("state_code_str", period)

        #  Parameters
        p = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.senior_or_disabled

        # Maine excludes savings up to a set amount (22 M.R.S. § 3174-AA(2)).
        # Its savings include bank accounts, stocks and bonds, which make up
        # all of the SSI countable resources modeled here.
        me = parameters(period).gov.states.me.dhhs.medicaid.savings_exclusion
        me_exclusion = where(is_couple, me.couple, me.individual)
        savings_exclusion = where(state == "ME", me_exclusion, 0)
        assets = max_(assets - savings_exclusion, 0)

        #  Asset limit
        state_limit = where(
            is_couple,
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
            is_couple,
            p.assets.limit.couple_limit_inclusive[state],
            p.assets.limit.individual_limit_inclusive[state],
        ).astype(bool)
        within_state_limit = where(
            inclusive, assets <= state_limit, assets < state_limit
        )
        return where(uses_msp_limit, within_msp_limit, within_state_limit)
