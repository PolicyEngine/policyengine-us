from policyengine_us.model_api import *
from policyengine_us.tools.state_eitc_helpers import (
    calculate_eitc_demographic_eligibility,
    calculate_eitc_max_agi_limit,
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
    )
    defined_for = StateCode.WA

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.wa.tax.income.credits.working_families_tax_credit
        # RCW 82.08.0206 pins Washington's WFTC to the federal EITC rules as
        # in effect on the date stored in
        # gov.states.wa.tax.income.credits.working_families_tax_credit.federal_eitc_snapshot_date
        # (currently 2022-06-09, the date the statute references).
        frozen_eitc = parameters.gov.irs.credits.eitc(p.federal_eitc_snapshot_date)
        person = tax_unit.members
        has_tin = person("has_tin", period)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        child_count = tax_unit.sum(
            person("is_qualifying_child_dependent", period) & has_tin
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
        frozen_investment_income_eligible = (
            tax_unit("eitc_relevant_investment_income", period)
            <= frozen_eitc.phase_out.max_investment_income
        )
        earnings = tax_unit("filer_adjusted_earnings", period)
        agi = tax_unit("adjusted_gross_income", period)
        higher_income = max_(earnings, agi)
        is_filer = eitc_filing_requirement_met(tax_unit, period)
        takes_up_eitc = tax_unit("takes_up_eitc", period)
        baseline_income_eligible = (earnings > 0) & (
            higher_income
            <= calculate_eitc_max_agi_limit(
                tax_unit, period, frozen_eitc, federal_child_count
            )
        )

        # Baseline eligibility: filers who qualify under the frozen 2022 IRC.
        eitc_eligible = (
            baseline_income_eligible
            & federal_demographic_eligible
            & federal_identification_eligible
            & frozen_investment_income_eligible
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
        state_only_income_eligible = (earnings > 0) & (
            higher_income
            <= calculate_eitc_max_agi_limit(tax_unit, period, frozen_eitc, child_count)
        )
        state_only_eitc_eligible = needs_state_only_path & (
            state_only_income_eligible
            & demographic_eligible
            & filer_has_tin
            & frozen_investment_income_eligible
            & is_filer
            & takes_up_eitc
        )

        # ESSB 6346 Sec. 901: age expansion eligibility (effective 2029)
        age_expansion_eligible = tax_unit(
            "wa_working_families_tax_credit_age_expansion_eligible", period
        )

        eligible = eitc_eligible | state_only_eitc_eligible | age_expansion_eligible

        # Parameters are based on EITC-eligible children.
        # WFTC child count is the larger of the federally-counted children
        # (SSN-eligible) and Washington-counted children (TIN-eligible).
        wftc_child_count = max_(federal_child_count, child_count)
        max_amount = p.amount.calc(wftc_child_count)
        # WFTC phases out at a certain amount below the EITC maximum AGI.
        # NB: The Revised Code of Washington is ambiguous:
        # "below the federal phase-out income"
        # The legislative analysis clarifies that this refers to "federal maximum AGI"
        # https://lawfilesext.leg.wa.gov/biennium/2021-22/Pdf/Bill%20Reports/House/1297-S.E%20HBR%20FBR%2021.pdf?q=20220706071752
        eitc_agi_limit = calculate_eitc_max_agi_limit(
            tax_unit, period, frozen_eitc, wftc_child_count
        )
        phase_out_start_reduction = p.phase_out.start_below_eitc.calc(wftc_child_count)
        phase_out_start = eitc_agi_limit - phase_out_start_reduction
        # The phase-out rates are hard-coded in the legal code, but HB 1888 (2021-22)
        # instructs DOR to revise it to get to the minimum amount by the EITC AGI limit.
        # https://app.leg.wa.gov/billsummary?BillNumber=1888&Year=2021&Initiative=false
        phase_out_rate = (max_amount - p.min_amount) / phase_out_start_reduction
        excess = max_(0, earnings - phase_out_start)
        reduction = max_(0, excess * phase_out_rate)
        phased_out_amount = max_amount - reduction
        # minimum benefit applies if calculated amount exceeds zero
        amount_if_eligible = where(
            phased_out_amount > 0, max_(p.min_amount, phased_out_amount), 0
        )
        return amount_if_eligible * eligible
