from policyengine_us.model_api import *
from policyengine_us.tools.state_eitc_helpers import (
    calculate_eitc_demographic_eligibility,
    eitc_filing_requirement_met,
    eitc_filing_status_eligible,
)


class wa_working_families_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Washington Working Families Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://app.leg.wa.gov/RCW/default.aspx?cite=82.08.0206",
        "https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/Senate%20Passed%20Legislature/6346-S.PL.pdf#page=61",
        # The (3)(c) $50 minimum-credit floor and the (3)(f) rate-setting rule
        # are on the next page.
        "https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/Senate%20Passed%20Legislature/6346-S.PL.pdf#page=62",
        # WAC 458-20-285 implements the WFTC and publishes the per-dollar
        # reduction rates; DOR's Excise Tax Advisory ETA 3240 lists the
        # per-year, per-child-count rates and the nearest-dollar rounding rule.
        "https://apps.leg.wa.gov/wac/default.aspx?cite=458-20-285",
        "https://dor.wa.gov/sites/default/files/2022-09/3240.pdf",
        # IRC 152(c)(3)(B), included in the federal EITC rules as in effect on
        # June 9, 2022, waives the qualifying-child age test for permanently
        # and totally disabled individuals.
        "https://www.law.cornell.edu/uscode/text/26/152#c_3_B",
    )
    defined_for = StateCode.WA

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.wa.tax.income.credits.working_families_tax_credit
        # RCW 82.08.0206(2)(d) pins Washington's WFTC to the federal EITC
        # rules as in effect on June 9, 2022. The snapshot date is a
        # statutory literal; policyengine-core parameters do not support
        # date-valued types, so the date appears here rather than in the
        # parameter tree.
        frozen_eitc = parameters.gov.irs.credits.eitc("2022-06-09")
        # The June 9, 2022 Internal Revenue Code still contains the EITC
        # inflation-adjustment provisions (26 U.S.C. 32(j)), so the
        # inflation-indexed dollar amounts (the investment-income limit here,
        # and the maximum qualifying income) track the current tax year, while
        # the structural rules (age band, disabled-dependent waiver,
        # separate-filer rule) stay on the frozen snapshot. Washington DOR
        # publishes the current-year federal investment-income limit each year.
        eitc = parameters(period).gov.irs.credits.eitc
        person = tax_unit.members
        has_tin = person("has_tin", period)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        # IRC 152(c)(3)(B) (part of the frozen 2022-06-09 federal EITC rules)
        # waives the age test for a permanently and totally disabled
        # dependent, matching the federal eitc_child_count.
        is_disabled_dependent = person("is_tax_unit_dependent", period) & person(
            "is_permanently_and_totally_disabled", period
        )
        child_count = tax_unit.sum(
            (person("is_qualifying_child_dependent", period) | is_disabled_dependent)
            & has_tin
        )
        filer_has_tin = tax_unit.sum(is_head_or_spouse & ~has_tin) == 0
        federal_identification_eligible = tax_unit(
            "filer_meets_eitc_identification_requirements", period
        )
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        federal_child_count = tax_unit("eitc_child_count", period)
        age = person("age", period)
        student = person("is_full_time_student", period)
        min_age = frozen_eitc.eligibility.age.min
        min_age_student = frozen_eitc.eligibility.age.min_student
        max_age = frozen_eitc.eligibility.age.max
        age_floor = where(student, min_age_student, min_age)
        demographic_eligible = (child_count > 0) | tax_unit.any(
            is_head_or_spouse & (age >= age_floor) & (age <= max_age)
        )
        federal_demographic_eligible = calculate_eitc_demographic_eligibility(
            tax_unit, period, frozen_eitc, federal_child_count
        )
        investment_income_eligible = (
            tax_unit("eitc_relevant_investment_income", period)
            <= eitc.phase_out.max_investment_income
        )
        earnings = tax_unit("filer_adjusted_earnings", period)
        agi = tax_unit("adjusted_gross_income", period)
        higher_income = max_(earnings, agi)
        maximum_qualifying_income = tax_unit(
            "wa_working_families_tax_credit_maximum_qualifying_income", period
        )
        is_filer = eitc_filing_requirement_met(tax_unit, period)
        takes_up_eitc = tax_unit("takes_up_eitc", period)
        # WAC 458-20-285(4) / Answer 4C: AGI must be strictly less than the
        # maximum qualifying income, so the ceiling test uses `<`. The baseline
        # and state-only paths share the same income test.
        income_eligible = (earnings > 0) & (higher_income < maximum_qualifying_income)

        # Baseline eligibility: filers who qualify under the frozen 2022 IRC.
        eitc_eligible = (
            income_eligible
            & federal_demographic_eligible
            & federal_identification_eligible
            & investment_income_eligible
            & eitc_filing_status_eligible(
                tax_unit,
                period,
                parameters,
                frozen_eitc.eligibility.separate_filer,
            )
            & is_filer
            & takes_up_eitc
        )
        needs_state_only_path = (
            (~federal_identification_eligible & filer_has_tin)
            | separate
            | (child_count > federal_child_count)
        )
        state_only_eitc_eligible = needs_state_only_path & (
            income_eligible
            & demographic_eligible
            & filer_has_tin
            & investment_income_eligible
            & is_filer
            & takes_up_eitc
        )

        # ESSB 6346 Sec. 901: age expansion eligibility (effective 2028)
        age_expansion_eligible = tax_unit(
            "wa_working_families_tax_credit_age_expansion_eligible", period
        )

        eligible = eitc_eligible | state_only_eitc_eligible | age_expansion_eligible

        # Parameters are based on EITC-eligible children.
        # WFTC child count is the larger of the federally-counted children
        # (SSN-eligible) and Washington-counted children (TIN-eligible).
        wftc_child_count = max_(federal_child_count, child_count)
        max_amount = p.amount.calc(wftc_child_count)
        # WFTC phases out at a certain amount below maximum qualifying income.
        # Before ESSB 6346, this is the frozen federal EITC maximum AGI.
        # From 2028 onward, it is the greater of that amount and the cash
        # assistance need standard for the tax household size.
        phase_out_start_reduction = p.phase_out.start_below_eitc.calc(wftc_child_count)
        phase_out_start = maximum_qualifying_income - phase_out_start_reduction
        # RCW 82.08.0206(3)(f) delegates the per-dollar reduction rate to DOR,
        # which sets it (via ETA 3240) at (maximum amount / phase-out band) so
        # the credit reaches the $50 statutory minimum at the maximum
        # qualifying income. WAC 458-20-285 Answer 10D publishes the resulting
        # 2022-base per-dollar rates ($0.12 for 0-1 children, $0.18 for 2,
        # $0.24 for 3+), which equal this ratio. The $50 minimum (RCW
        # 82.08.0206(3)(c)) then floors any positive reduced amount.
        phase_out_rate = max_amount / phase_out_start_reduction
        # Modeling choice: the reduction is measured against the greater of
        # earned income or AGI, the same measure used for the
        # maximum-qualifying-income ceiling above. RCW 82.08.0206(2)(b) defines
        # "income" as earned income (26 U.S.C. Sec. 32), so using the greater
        # of earned income and AGI is not the statutory base; it can
        # over-reduce households whose AGI exceeds their earned income inside
        # the band. Aligning the reduction base to earned income alone is a
        # follow-up.
        excess = max_(0, higher_income - phase_out_start)
        reduction = excess * phase_out_rate
        phased_out_amount = max_amount - reduction
        # RCW 82.08.0206(3)(b): the reduced refund is rounded to the nearest
        # dollar. The $50 statutory minimum (RCW 82.08.0206(3)(c)) gates on the
        # UNROUNDED amount, so a positive amount that rounds toward zero still
        # floors to $50 rather than dropping to $0. This also makes the floor
        # residue-proof against float error exactly at the ceiling
        # (Sec. 901(2)(a)(ii)(C)).
        amount_if_eligible = where(
            phased_out_amount > 0,
            max_(p.min_amount, round_(phased_out_amount)),
            0,
        )
        return amount_if_eligible * eligible
