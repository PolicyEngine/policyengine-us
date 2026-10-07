from policyengine_us.model_api import *


class medicaid_ltss_csra_resource_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets modeled Medicaid LTSS resource threshold"
    definition_period = MONTH
    documentation = (
        "Tests comprehensive LTSS resources derived from each person's "
        "own countable-resource inventory. Texas "
        "and Delaware use the SSI resource limits (1 TAC 358.323 and "
        "358.437; DSSM 20100.2.2 and 20300); Washington uses its own "
        "resource standard (WAC 182-513-1350). For an applicant with a "
        "community spouse, the initial CSRA is the greater of the applicable "
        "floor or the fixed statutory one-half of the couple's snapshot "
        "resources under 42 USC 1396r-5(c)(1)(A)(ii) and (f)(2)(A), capped "
        "at the federal maximum. Texas and Delaware use the first-period "
        "snapshot; Washington uses the first day of the beginning month "
        "of the most recent continuous period under WAC 182-513-1355(2)-(4). "
        "Washington instead allocates the federal maximum for continuous "
        "periods starting October 1989 through July 2003. For pre-October "
        "1989 periods there is no CSRA: at both initial and continuing "
        "determinations, one-half of the sum of applicant-sole resources "
        "and the full jointly titled balance is tested against the individual limit, "
        "excluding spouse-sole resources. Those ownership balances are "
        "separate leaf inputs because attributed totals do not reveal title. "
        "There is a new determination after a break of at least 30 consecutive "
        "days under WAC 182-513-1350(3)(b)(vi)(A). Texas uses the federal minimum as its "
        "floor; Delaware's $25,000 state spousal share (DSSM 20910.10) sits "
        "below the federal minimum, which therefore governs; Washington's "
        "state spousal resource standard sits above it. Initial eligibility "
        "tests both spouses' current resources against the CSRA plus the "
        "applicant's resource limit. For periods starting on or after October "
        "1989, after the eligibility month in the same "
        "continuous LTSS period, set "
        "medicaid_ltss_is_initial_eligibility_determination to false: only "
        "the applicant's resources count against the individual limit, "
        "without community spouse resources or a CSRA, under 42 USC "
        "1396r-5(c)(4) and DSSM 20980. Court and "
        "fair-hearing adjustments, resource-hardship overrides, and "
        "detailed state asset exclusions are not modeled."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396r-5#f_2",
        "https://www.govinfo.gov/content/pkg/USCODE-2024-title42/html/USCODE-2024-title42-chap7-subchapXIX-sec1396r-5.htm",
        "https://www.law.cornell.edu/regulations/texas/1-Tex-Admin-Code-SS-358-323",
        "https://fhb.hhs.texas.gov/sites/default/files/documents/mepd-26-2.pdf#page=465",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=10",
        "https://dhss.delaware.gov/wp-content/uploads/sites/11/2026/06/2026-SSI-Related-Income-Standards-and-Medicare-Premiums.pdf#page=2",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=69",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=71",
        "https://app.leg.wa.gov/wac/default.aspx?cite=182-513-1350",
        "https://app.leg.wa.gov/wac/default.aspx?cite=182-513-1355",
        "https://www.hca.wa.gov/assets/free-or-low-cost/income-standards-20260101.pdf#page=3",
    )

    def formula_2026_01_01(person, period, parameters):
        p = parameters(period).gov.hhs.medicaid.eligibility.long_term_care.financial
        state = person.household("state_code", period)
        states = state.possible_values
        pathway = person("medicaid_ltss_financial_pathway", period)
        pathways = pathway.possible_values
        assistance_unit_size = person("medicaid_ltss_assistance_unit_size", period)
        resources = person("medicaid_ltss_countable_resources", period)

        ssi_resource_limit = parameters(period).gov.ssa.ssi.eligibility.resources.limit
        texas_or_delaware = (state == states.TX) | (state == states.DE)
        resource_limit = select(
            [
                texas_or_delaware & (assistance_unit_size == 1),
                texas_or_delaware & (assistance_unit_size == 2),
                (state == states.WA) & (assistance_unit_size == 1),
            ],
            [
                ssi_resource_limit.individual,
                ssi_resource_limit.couple,
                p.wa.resources.individual,
            ],
            default=0,
        )
        no_community_spouse_eligible = resources <= resource_limit

        csra = person("medicaid_ltss_csra", period)
        current_couple_resources = resources + person(
            "medicaid_ltss_community_spouse_countable_resources",
            period,
        )
        has_community_spouse = person("medicaid_ltss_has_community_spouse", period)
        is_initial_determination = person(
            "medicaid_ltss_is_initial_eligibility_determination", period
        )
        community_spouse_eligible = (assistance_unit_size == 1) & where(
            is_initial_determination,
            current_couple_resources <= csra + resource_limit,
            resources <= resource_limit,
        )
        start_year = person(
            "wa_medicaid_ltss_most_recent_institutionalization_start_year", period
        )
        start_month = person(
            "wa_medicaid_ltss_most_recent_institutionalization_start_month", period
        )
        onset = start_year * 100 + start_month
        valid_onset = (
            (start_year >= 1)
            & (start_month >= 1)
            & (start_month <= 12)
            & (onset <= period.start.year * 100 + period.start.month)
        )
        # WAC 182-513-1355(2)(a) counts one-half of the sum of applicant-sole
        # resources and the full joint balance, excluding spouse-sole resources. This
        # rule continues for pre-1989 periods at redeterminations as well.
        pre_1989_resources = (
            person("wa_medicaid_ltss_solely_owned_countable_resources", period)
            + person("wa_medicaid_ltss_jointly_owned_countable_resources", period)
        ) / 2
        community_spouse_eligible = where(
            (state == states.WA) & (onset < 198910),
            (assistance_unit_size == 1) & (pre_1989_resources <= resource_limit),
            community_spouse_eligible,
        ) & ((state != states.WA) | valid_onset)
        modeled_pathway = pathway != pathways.UNMODELED

        return modeled_pathway & where(
            has_community_spouse,
            community_spouse_eligible,
            no_community_spouse_eligible,
        )
