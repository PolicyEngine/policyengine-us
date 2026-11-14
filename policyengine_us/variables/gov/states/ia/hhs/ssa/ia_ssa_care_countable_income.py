from policyengine_us.model_api import *
from policyengine_us.variables.gov.states._spouses import (
    state_couple_total,
    state_is_married,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_couple_total,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)


class ia_ssa_care_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Iowa SSA care countable income without general disregard"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.IA
    documentation = "Care income without the $20 general exclusion: SSI countable income plus SSI. In-home care counts an adult's spouse's income. An eligible family-life home couple, and a residential care couple in the month of entry, split the couple's income. A retained prior-SSI entry couple now living apart uses the SSI couple amount calculated from its combined income. After the month of entry, a married resident counts own income plus the SSI individual amount from it. A child in in-home care receives income deemed from parents under the Iowa method. Interest and dividends are excluded. First-month deeming from an ineligible spouse, and deductions absent from the federal SSI income inputs, are not modeled."
    reference = (
        # 441 IAC 52.1(3)"a"
        "https://www.legis.iowa.gov/docs/iac/chapter/441.52.pdf#page=1",
        # PDF pages 34, 40-42, 46, 49, 58-65, 67-71
        "https://hhs.iowa.gov/media/3987/download?inline=#page=34",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ia.hhs.ssa
        ssi = parameters(period).gov.ssa.ssi
        category = person("ia_ssa_category", period)
        c = category.possible_values
        home = category == c.IN_HOME_CARE
        rcf = category == c.RESIDENTIAL_CARE
        joint = person("ssi_couple_computation_applies", period)
        spouse = person("ia_ssa_has_spouse", period)
        adult = ~person("is_child", period.this_year)
        combine = select(
            [home, rcf],
            [adult & spouse, person("ia_ssa_rcf_couple_budget", period)],
            default=joint,
        )
        # NOTE: 441 IAC 52.1(3)"a"(1) deducts "impairment-related work
        # expenses, as defined by SSI plus $65 plus one-half of any remaining
        # earned income" (6-B p.65, Mr. L). Neither federal SSI nor this
        # variable models those expenses (issue 3669). For a resident without
        # SSI, entering one-half of them in ia_ssa_care_additional_deductions
        # reproduces the rule (ia_ssa.yaml Case 62). For an SSI recipient,
        # SSA's payment rises by the same one-half, so care income does not
        # change (6-B p.59).
        earned = max_(
            person("ssi_earned_income", period)
            - person("ssi_blind_or_disabled_working_student_exclusion", period),
            0,
        )
        # NOTE: 20 CFR 416.1124(c)(22) excludes "Interest and dividend income
        # from a countable resource", as Manual 8-E Dividends and Interest
        # Income do. Federal SSI still counts them (issue 10079), so the
        # sources in excluded_unearned_sources are dropped here and from the
        # family-life home $20 test in ia_ssa (ia_ssa.yaml Case 74 for
        # residential care income and Case 63 for the $20 test).
        # Remove the list once issue 10079 is fixed, or they are excluded
        # twice. SMME income (ia_ssa_smme_countable_income) and the SSA-paid
        # amounts (ia_ssa_federal) use SSI countable income, so they count
        # interest and dividends until then. The 8-E exceptions for excluded
        # resources are not modeled.
        # NOTE: 6-B excludes one-third of child support a child receives from
        # an absent parent. Federal SSI does not apply 20 CFR 416.1124(c)(11)
        # yet (issue 10242), so the shared federal share is read here; remove
        # it once issue 10242 is fixed.
        unearned = max_(
            person("ssi_unearned_income", period)
            - add(person, period, p.excluded_unearned_sources)
            - ~adult
            * person("child_support_received", period)
            * ssi.income.exclusions.child_support_share,
            0,
        )
        # 6-B: "do not rely on SSI deeming calculations for children" in
        # in-home health-related care; other care uses SSI parental deeming.
        deemed = where(
            home,
            person("ia_ssa_income_deemed_from_parents", period),
            person("ssi_unearned_income_deemed_from_ineligible_parent", period),
        )
        unearned = unearned + ~adult * deemed
        # NOTE: 6-B pp.60-61 treats spouses "as individuals beginning the month
        # after the month of entry", and the examples on pp.68-71 then use the
        # resident's own SSI (Mr. K: "$ 839 SSI benefit"). A resident whose
        # income is below the SSI rate "must now apply for and accept SSI
        # benefits" (p.61). The model therefore assumes SSA pays each spouse as
        # an individual from that month, and credits that amount even to a
        # resident who does not take up SSI. The SSI individual amount is
        # computed here from the resident's own income
        # (ia_ssa.yaml Cases 57, 58, 60 and 73).
        individual_ssi = max_(
            ssi.amount.individual
            - _apply_ssi_exclusions(
                earned * MONTHS_IN_YEAR,
                unearned * MONTHS_IN_YEAR,
                parameters,
                period,
            )
            / MONTHS_IN_YEAR,
            0,
        )
        separated = (
            rcf
            & state_is_married(person, period.this_year)
            & ~person("ia_ssa_care_initial_partial_month", period)
        )
        benefit = where(separated, individual_ssi, person("ssi", period))
        # RCF's prior-SSI entry budget retains the marriage across facilities;
        # other care paths pool only with the spouse living in the home.
        earned = where(
            combine,
            where(
                rcf,
                state_couple_total(person, period.this_year, earned),
                _ssi_couple_total(person, period.this_year, earned),
            ),
            earned,
        )
        unearned = where(
            combine,
            where(
                rcf,
                state_couple_total(person, period.this_year, unearned),
                _ssi_couple_total(person, period.this_year, unearned),
            ),
            unearned,
        )
        benefit = where(
            combine,
            where(
                rcf,
                state_couple_total(person, period.this_year, benefit),
                _ssi_couple_total(person, period.this_year, benefit),
            ),
            benefit,
        )
        # 6-B's entry-month example (PDF p.69) retains couple SSI of 1,236
        # for pensions of 175 and 100: 1,491 - (275 - 20). Current separate
        # households make federal SSI individual immediately in this static
        # model, so pooling those payments would overstate entry-month care
        # income. Reconstruct only this retained Iowa entry budget, as the
        # individual RCF amount above is reconstructed after entry. This uses
        # the regular RCF SSI rate and the income inputs already used for
        # care; it does not change federal timing or the documented gaps.
        retained_entry_ssi = max_(
            ssi.amount.couple
            - _apply_ssi_exclusions(
                earned * MONTHS_IN_YEAR,
                unearned * MONTHS_IN_YEAR,
                parameters,
                period,
            )
            / MONTHS_IN_YEAR,
            0,
        )
        benefit = where(rcf & combine & ~spouse, retained_entry_ssi, benefit)
        income = (
            _apply_ssi_exclusions(
                earned * MONTHS_IN_YEAR,
                unearned * MONTHS_IN_YEAR,
                parameters,
                period,
                general_exclusion=0,
            )
            / MONTHS_IN_YEAR
            + benefit
        )
        return where(combine & ~home, income / 2, income)
