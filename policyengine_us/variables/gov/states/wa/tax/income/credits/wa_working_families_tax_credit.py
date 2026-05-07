from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.credits.eitc_helpers import (
    calculate_eitc_like_amount,
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
        min_age = parameters.gov.irs.credits.eitc.eligibility.age.min(period)
        min_age_student = parameters.gov.irs.credits.eitc.eligibility.age.min_student(
            period
        )
        max_age = parameters.gov.irs.credits.eitc.eligibility.age.max(period)
        age_floor = where(student, min_age_student, min_age)
        demographic_eligible = (child_count > 0) | tax_unit.any(
            is_head_or_spouse & (age >= age_floor) & (age <= max_age)
        )

        # Baseline eligibility: filers who claim EITC
        eitc = tax_unit("eitc", period)
        eitc_eligible = eitc > 0
        needs_state_only_path = (
            (~federal_identification_eligible & filer_has_tin)
            | separate
            | (child_count > federal_child_count)
        )
        state_only_eitc_eligible = needs_state_only_path & (
            calculate_eitc_like_amount(
                tax_unit,
                period,
                parameters,
                child_count,
                demographic_eligible,
                filer_has_tin,
                separate_filer_eligible=True,
            )
            > 0
        )

        # ESSB 6346 Sec. 901: age expansion eligibility (effective 2029)
        age_expansion_eligible = tax_unit(
            "wa_working_families_tax_credit_age_expansion_eligible", period
        )

        eligible = eitc_eligible | state_only_eitc_eligible | age_expansion_eligible

        # Parameters are based on EITC-eligible children.
        p = parameters(
            period
        ).gov.states.wa.tax.income.credits.working_families_tax_credit
        eitc_child_count = max_(federal_child_count, child_count)
        max_amount = p.amount.calc(eitc_child_count)
        # WFTC phases out at a certain amount below the EITC maximum AGI.
        # NB: The Revised Code of Washington is ambiguous:
        # "below the federal phase-out income"
        # The legislative analysis clarifies that this refers to "federal maximum AGI"
        # https://lawfilesext.leg.wa.gov/biennium/2021-22/Pdf/Bill%20Reports/House/1297-S.E%20HBR%20FBR%2021.pdf?q=20220706071752
        eitc_parameters = parameters(period).gov.irs.credits.eitc
        phase_out_start = eitc_parameters.phase_out.start.calc(eitc_child_count)
        phase_out_start += tax_unit("tax_unit_is_joint", period) * eitc_parameters.phase_out.joint_bonus.calc(
            eitc_child_count
        )
        eitc_agi_limit = phase_out_start + eitc_parameters.max.calc(
            eitc_child_count
        ) / eitc_parameters.phase_out.rate.calc(eitc_child_count)
        eitc_agi_limit = max_(tax_unit("eitc_agi_limit", period), eitc_agi_limit)
        phase_out_start_reduction = p.phase_out.start_below_eitc.calc(eitc_child_count)
        phase_out_start = eitc_agi_limit - phase_out_start_reduction
        # The phase-out rates are hard-coded in the legal code, but HB 1888 (2021-22)
        # instructs DOR to revise it to get to the minimum amount by the EITC AGI limit.
        # https://app.leg.wa.gov/billsummary?BillNumber=1888&Year=2021&Initiative=false
        phase_out_rate = (max_amount - p.min_amount) / phase_out_start_reduction
        earnings = tax_unit("filer_adjusted_earnings", period)
        excess = max_(0, earnings - phase_out_start)
        reduction = max_(0, excess * phase_out_rate)
        phased_out_amount = max_amount - reduction
        # minimum benefit applies if calculated amount exceeds zero
        amount_if_eligible = where(
            phased_out_amount > 0, max_(p.min_amount, phased_out_amount), 0
        )
        return amount_if_eligible * eligible
