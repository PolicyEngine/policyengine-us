from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.wy.dfs.ccap.wy_ccap_day_length import (
    WYCCAPDayLength,
)


class wy_ccap_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Wyoming CCAP monthly family copayment"
    definition_period = MONTH
    defined_for = "wy_ccap_eligible"
    reference = (
        "https://dfs.wyo.gov/services/family-services/child-care/",  # Wyoming DFS Table I - Child Care Sliding Fee Scale, eff. 04/01/25-03/31/26 (single page)
        "https://wyoleg.gov/statutes/compress/title42.pdf#page=13",  # W.S. 42-2-103(f)(i) (enabling authority for the sliding fee scale copayments)
        "https://drive.google.com/file/d/10TJ3S8d_nwyNxdkkbyk2gzCfHTk7CTcA/view#page=34",  # Wyoming CCDF State Plan FFY 2025-2027 §3.1.1 7% of gross family income cap (PDF p. 34), §3.2.1 fee is per child up to a maximum per family (p. 36), §3.3.1.vi copayments waived for foster, kinship, and protective-services children (p. 37)
    )

    def formula(spm_unit, period, parameters):
        # Table I: a flat daily DFS parental copay per child, keyed by the
        # unit's Sliding Fee Scale step (a federal-poverty-guideline ratio
        # band) and the child's part- or full-day care, assessed for each
        # attended day. Units at or below 100% of the guideline (Step 1) owe
        # no copay per W.S. 42-2-103(f)(i)(A).
        p = parameters(period).gov.states.wy.dfs.ccap.copay
        countable_income = spm_unit("wy_ccap_countable_income", period)
        fpg = spm_unit("spm_unit_fpg", period)
        fpg_ratio = np.divide(
            countable_income,
            fpg,
            out=np.zeros_like(countable_income, dtype=float),
            where=fpg > 0,
        )
        person = spm_unit.members
        person_ratio = spm_unit.project(fpg_ratio)
        full_day = person("wy_ccap_day_length", period) == WYCCAPDayLength.FULL_DAY
        daily_copay = where(
            full_day,
            p.full_day.calc(person_ratio),
            p.part_day.calc(person_ratio),
        )
        care_days = person("childcare_attending_days_per_month", period.this_year)
        is_eligible_child = person("wy_ccap_eligible_child", period)
        family_copay = spm_unit.sum(daily_copay * care_days * is_eligible_child)
        # CCDF State Plan §3.1.1: the family copayment does not exceed 7% of
        # gross family income; the base floors at zero so a negative gross
        # income (a self-employment loss) cannot produce a negative copay.
        gross_income = max_(spm_unit("wy_ccap_gross_income", period), 0)
        capped_copay = min_(family_copay, p.family_income_cap_rate * gross_income)
        # W.S. 42-2-103(f)(i)(A) / CCDF State Plan §3.3.1.vi: the copay is
        # waived for foster, kinship, and protective-services children, whose
        # income is deemed at or below 100% of the guideline.
        #
        # Simplification, deliberate: the waiver is applied to the whole
        # assistance unit rather than to the qualifying child alone, matching
        # wy_ccap_income_eligible. Rules §8(e)(iv)(C) scopes the income
        # exclusion to the foster child while §8(e)(iv)(A) still counts the
        # parent's income for the household's own children, so in a mixed unit
        # the law would charge the own child a copay at the family's step while
        # the foster child pays nothing. Here one qualifying child zeroes the
        # whole family's copay: a Step 4 unit with one foster and one own child
        # in full-day care 20 days each is modeled at $0 rather than
        # $6.40 x 20 = $128 per month for the own child. Per-child treatment
        # would require income eligibility determined per child, with the
        # deemed child taking a guideline ratio of zero (Step 1, $0). No source
        # states the mixed-unit case outright and such units are uncommon, so
        # the unit-wide reading is retained.
        waived = spm_unit.any(
            person("is_in_foster_care", period)
            | person("receives_or_needs_protective_services", period.this_year)
        )
        return where(waived, 0, capped_copay)
