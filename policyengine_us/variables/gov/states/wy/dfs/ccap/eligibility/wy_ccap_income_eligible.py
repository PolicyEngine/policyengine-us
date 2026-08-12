from policyengine_us.model_api import *


class wy_ccap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Income eligible for Wyoming Child Care, Purchase of Service"
    definition_period = MONTH
    defined_for = StateCode.WY
    reference = (
        "https://rules.wyo.gov/DownloadFile.aspx?source_id=24638&source_type_id=81&doc_type_id=110&include_meta_data=Y&file_type=pdf&filename=24638.pdf&token=189087205215053222164006221008072207044097222254",  # Wyo. Admin. Rules, DFS, Child Care - Purchase of Service, Ch. 1 §8(e)(i)(N), §8(e)(iv)(C) and Appendix A, eff. 05/07/2025 (PDF pp. 18, 19, 37)
        "https://dfs.wyo.gov/about/policy-manuals/child-care-subsidy-policy-manual/",  # Wyoming DFS Child Care Subsidy Policy Manual §1101.A (Ch. 1100 PDF p. 1) and §1201.B (Ch. 1200 PDF p. 1)
        "https://drive.google.com/file/d/10TJ3S8d_nwyNxdkkbyk2gzCfHTk7CTcA/view#page=18",  # Wyoming CCDF State Plan FFY 2025-2027 §§2.2.2.f, 2.2.2.g (PDF p. 18)
    )

    def formula(spm_unit, period, parameters):
        # Manual §1101.A: an initial application must fall at Sliding Fee
        # Scale Step 4 or below (175% of the federal poverty guideline).
        # Rules §8(e)(i)(N)(II) lets a unit already receiving assistance
        # continue through Steps 5-6 (up to 225%) "when the gross income has
        # increased due to employment"; Manual §1201.B states the operating
        # rule without that condition, allowing the graduated phaseout
        # whenever countable income stays within Step 6 with no 30-or-more-day
        # break in aid. The wy_ccap_enrolled input proxies continuing-recipient
        # status; neither the cause of the income increase nor the break in aid
        # is tracked. The Table I bands equal the guideline times the step
        # multiplier, so the limits self-uprate; each chart takes effect
        # April 1 while spm_unit_fpg applies the calendar-year guideline, a
        # three-month timing simplification.
        p = parameters(period).gov.states.wy.dfs.ccap.income
        countable_income = spm_unit("wy_ccap_countable_income", period)
        fpg = spm_unit("spm_unit_fpg", period)
        enrolled = spm_unit("wy_ccap_enrolled", period)
        fpg_share = where(enrolled, p.fpl_limit.continued, p.fpl_limit.initial)
        income_eligible = countable_income <= fpg * fpg_share
        # Manual §502: POWER and Tribal TANF recipients are categorically
        # eligible.
        tanf_enrolled = spm_unit("is_tanf_enrolled", period)
        # Rules §8(e)(iv)(C): "A foster parent's income shall not be
        # considered in determining eligibility for a foster child." CCDF
        # State Plan §2.2.2.g waives the income eligibility requirement for
        # children who receive or need protective services, a definition
        # §2.2.2.f extends to foster care, kinship care, court supervision,
        # and homelessness; §3.3.1.vi deems those children at or below 100% of
        # the guideline. Excluding the foster parent's income leaves the child
        # with no countable income, so the waiver is modeled as passing the
        # income test. Rules §8(e)(iii)(A) keeps the child in the caretaker's
        # unit, so this is applied unit-wide rather than per child: a
        # non-foster sibling in the same unit also passes, where §8(e)(iv)(A)
        # would still count the parent's income for that child. wy_ccap_copay
        # applies the same simplification and quantifies its effect. The
        # activity and child tests continue to apply (Plan §2.2.2.h, Rules
        # §8(e)(i)(J)).
        person = spm_unit.members
        income_waived = spm_unit.any(
            person("is_in_foster_care", period)
            | person("receives_or_needs_protective_services", period.this_year)
        )
        return income_eligible | tanf_enrolled | income_waived
