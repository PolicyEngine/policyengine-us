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
        "https://dfs.wyo.gov/services/family-services/child-care/",  # Wyoming CCDF State Plan FFY 2025-2027 §§3.1.1, 3.3.1 (PDF pp. 34, 37)
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
        # W.S. 42-2-103(f)(i)(A) / CCDF State Plan §3.3.1: the copay is waived
        # for foster, kinship, and protective-services children, whose income
        # is treated as at or below 100% of the guideline.
        waived = spm_unit.any(
            person("is_in_foster_care", period)
            | person("receives_or_needs_protective_services", period.this_year)
        )
        return where(waived, 0, capped_copay)
