from policyengine_us.model_api import *


class wy_ccap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Wyoming CCAP countable income"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.WY
    reference = (
        "https://rules.wyo.gov/DownloadFile.aspx?source_id=24638&source_type_id=81&doc_type_id=110&include_meta_data=Y&file_type=pdf&filename=24638.pdf&token=189087205215053222164006221008072207044097222254",  # Wyo. Admin. Rules, DFS, Child Care - Purchase of Service, Ch. 1 §8(e)(iv)(D), eff. 05/07/2025 (PDF p. 19)
        "https://dfs.wyo.gov/about/policy-manuals/child-care-subsidy-policy-manual/",  # Wyoming DFS Child Care Subsidy Policy Manual §§905, 907 (PDF pp. 5-9)
    )

    def formula(spm_unit, period, parameters):
        # Rules Ch. 1 §8(e)(iv)(D): countable income is gross earned plus
        # gross unearned income from the counted sources, less allowable
        # deductions. Manual §§902-903 deduct 25% of gross self-employment
        # receipts or actual business expenses, whichever benefits the
        # client; self_employment_income is already net of actual expenses,
        # matching the actual-expense branch, and PolicyEngine has no
        # gross-receipts input, so the fixed-25% alternative is not modeled.
        p = parameters(period).gov.states.wy.dfs.ccap.income
        person = spm_unit.members
        # The earned rows of the counted sources
        # (income/countable_income/sources.yaml).
        earned = add(
            person,
            period,
            [
                "employment_income",
                "self_employment_income",
                "sstb_self_employment_income",
                "farm_operations_income",
            ],
        )
        # Appendix B exempts the wages of a dependent child under 18, while
        # Rules Ch. 1 §8(e)(iv)(E)(II) and Manual §905.A.6 count a minor
        # parent's own income, so the exemption reaches only minors who are
        # not themselves parents (own child in the household).
        is_child = person("is_child", period.this_year)
        is_minor_parent = is_child & person("is_parent", period.this_year)
        # Rules Ch. 1 §4(aa), §8(e)(iv)(D)(III)(5.): deduct $200 from the
        # gross earned income of each employed adult, capped at that adult's
        # earnings; the per-person zero floor also keeps a self-employment
        # loss from offsetting other income. A minor parent is not an adult
        # (Manual §200 defines an adult as 18 or over, or emancipated —
        # emancipation is not tracked), so a minor parent's earnings count
        # in full with no disregard.
        countable_earned = select(
            [~is_child, is_minor_parent],
            [max_(earned - p.earned_income_disregard, 0), max_(earned, 0)],
            default=0,
        )
        unearned = spm_unit("wy_ccap_gross_income", period) - spm_unit.sum(earned)
        # Manual §907.B: deduct child support paid by a parent whose income
        # counts, capped at the monthly court-ordered amount and excluding
        # arrears; the court-ordered amount and arrears are not tracked, so
        # the full support paid is deducted.
        child_support = add(spm_unit, period, ["child_support_expense"])
        return max_(spm_unit.sum(countable_earned) + unearned - child_support, 0)
