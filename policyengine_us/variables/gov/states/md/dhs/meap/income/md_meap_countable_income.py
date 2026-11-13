from policyengine_us.model_api import *


class md_meap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Maryland MEAP countable household income"
    unit = USD
    defined_for = StateCode.MD
    reference = (
        "https://regs.maryland.gov/us/md/exec/comar/07.03.21.04",
        # PDF pages 111, 112.
        "https://dhs.maryland.gov/documents/OHEP/OHEP-Operations-Manual.pdf#page=111",
        # PDF pages 6, 7.
        "https://liheapch.acf.gov/docs/2026/state-plans/MD_Plan_2026.pdf#page=6",
    )
    documentation = (
        "Annual income approximates the 30-day application period. All members' income "
        "counts in full. Follows COMAR where the checklists differ: nonrecurring lump "
        "sums and AmeriCorps/VISTA are excluded although the manual and plan count "
        "them; interest and dividends count although the plan leaves them unchecked; "
        "strike funds without employee contributions count although manual "
        "Attachment B excludes them. Reported child support paid is assumed "
        "court-ordered. Veterans income approximates pension benefits and strike "
        "income is assumed not employee-funded. Social Security and railroad "
        "retirement count net of the computed Medicare Part B premium. Each source is "
        "floored at zero, so a rental or estate loss does not offset other income. "
        "TDAP, royalties, gifts, loans, special allowances and home-care receipts "
        "cannot be isolated reliably."
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.md.dhs.meap.income
        person = spm_unit.members
        # COMAR 07.03.21.04D(3), D(26) and E(20) count Social Security and
        # railroad retirement benefits less the Medicare payment deduction, and
        # plan 1.9 (page 6) checks "Excluding MediCare deduction". The computed
        # medicare_part_b_premium is the out-of-pocket Part B premium, zero when
        # a Medicare Savings Program pays it.
        benefits = spm_unit.sum(
            max_(
                person("social_security", period)
                + person("railroad_benefits", period)
                - person("medicare_part_b_premium", period),
                0,
            )
        )
        # COMAR 07.03.21.04D(2) treats self-employment and rental income as one
        # item and plan 1.8 (page 6) counts gross income, so each unearned
        # source is floored like the earned sources: a loss in one source
        # cannot offset another. The TANF source applies take-up to Maryland
        # TCA entitlement.
        unearned = 0
        for source in p.sources.unearned:
            unearned = unearned + max_(add(spm_unit, period, [source]), 0)
        income = (
            add(spm_unit, period, ["md_meap_countable_earned_income"])
            + benefits
            + unearned
        )
        return max_(income - add(spm_unit, period, ["child_support_expense"]), 0)
