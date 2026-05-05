from policyengine_us.model_api import *


class ia_ssa(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Iowa State Supplementary Assistance"
    unit = USD
    defined_for = StateCode.IA
    reference = (
        "https://www.legis.iowa.gov/docs/code/249.3.pdf",
        "https://www.legis.iowa.gov/docs/iac/chapter/01-07-2026.441.52.pdf",
        "https://hhs.iowa.gov/media/15607/download",
        "https://hhs.iowa.gov/assistance-programs/state-supplementary-assistance",
    )

    def formula(person, period, parameters):
        arrangement = person("ia_ssa_living_arrangement", period)
        arr_values = arrangement.possible_values
        p = parameters(period).gov.states.ia.hhs.ssa
        # YEAR-defined FLOW variables auto-divide to monthly when requested
        # at a MONTH period (policyengine-core simulation.calculate_divide).
        countable_monthly = person("ssi_countable_income", period)
        ssi_monthly = person("ssi", period)
        # Iowa RCF, FLH-eligibility, and IHHRC do not allow the SSI $20 general
        # income disregard (GL 6-B-46 pp. 30, 36–38, 54–58). RCF and IHHRC are
        # state-administered, so this helper restores the $20 the SSI exclusion
        # already removed.
        countable_no_disregard = person("ia_ssa_countable_income_no_disregard", period)
        p_ssi = parameters(period).gov.ssa.ssi.amount
        individual_fbr = p_ssi.individual
        couple_fbr = p_ssi.couple
        # BLIND — IAC 441—52.1(4): flat $22 state supplement (frozen since 2011).
        # Federally administered, so SSA's $20 disregard applies via
        # ssi_countable_income.
        blind_amt = max_(
            0, (individual_fbr + p.blind) - max_(countable_monthly, individual_fbr)
        )
        # DP — IAC 441—52.1(2): per-configuration assistance standard. Pick the
        # applicable Federal Benefit Rate (couple FBR for configurations that
        # include an eligible spouse, individual FBR otherwise) so the
        # supplement equals (standard − max(countable, applicable_fbr)).
        dp_config = person("ia_ssa_dp_configuration", period)
        dp_config_values = dp_config.possible_values
        dp_assistance_standard = p.dp.assistance_standard[dp_config]
        dp_has_spouse = (
            (dp_config == dp_config_values.AGED_OR_DISABLED_WITH_SPOUSE_AND_DEPENDENT)
            | (
                dp_config
                == dp_config_values.BLIND_WITH_AGED_OR_DISABLED_SPOUSE_AND_DEPENDENT
            )
            | (dp_config == dp_config_values.BLIND_WITH_BLIND_SPOUSE_AND_DEPENDENT)
        )
        dp_applicable_fbr = where(dp_has_spouse, couple_fbr, individual_fbr)
        # Couple-config DP compares income against couple_fbr, which is a
        # marital-unit-level threshold. countable_monthly is per-spouse
        # (combined / 2 for joint SSI claims), so aggregate across the
        # marital unit when the comparison threshold is couple-level.
        marital_countable = person.marital_unit.sum(countable_monthly)
        dp_compare_income = where(dp_has_spouse, marital_countable, countable_monthly)
        dp_amt_full = max_(
            0,
            dp_assistance_standard - max_(dp_compare_income, dp_applicable_fbr),
        )
        # Per-marital-unit guard: couple-FBR DP configurations describe the
        # whole marital unit, not each spouse. Split the supplement equally
        # among spouses in the marital unit who claim a couple-FBR config so
        # the SPM-unit aggregation does not double-count when both spouses
        # set the same couple configuration.
        dp_couple_count = person.marital_unit.sum(dp_has_spouse)
        dp_divisor = where(dp_has_spouse, max_(dp_couple_count, 1), 1)
        dp_amt = dp_amt_full / dp_divisor
        # FLH — IAC 441—52.1(1): SSA-administered, so the V-shape uses
        # ssi_countable_income (with the $20 disregard SSA actually applies).
        # The $142 SSA cap caps the federally-administered piece; for SSI-only
        # recipients (no unearned income to absorb the $20 disregard), the
        # Department pays the (state_supplement − cap) gap so total income
        # reaches the standard (GL 6-B-46 p.30). 441—52.1(4) excludes the $22
        # blind allowance for recipients of any other SSP, so blind FLH
        # recipients receive the FLH benefit only — no $22 stack.
        flh_v_shape = max_(
            0,
            (individual_fbr + p.flh.state_supplement)
            - max_(countable_monthly, individual_fbr),
        )
        flh_base = min_(flh_v_shape, p.flh.max_supplement)
        flh_extra = where(
            countable_monthly < 0.01,
            max_(0, p.flh.state_supplement - p.flh.max_supplement),
            0,
        )
        flh_amt = flh_base + flh_extra
        # RCF — IAC 441—52.1(3): cost-of-care minus client participation.
        # Client participation = total monthly income (countable + SSI) minus
        # the personal needs allowance. Iowa GL 6-B-46 p. 54 omits the SSI $20
        # disregard, so use countable_no_disregard. Other regulatory deductions
        # (impairment-related work expenses, dependent diversions, unmet
        # medical needs, first-month expenses) are not modeled.
        rcf_per_diem = person("ia_ssa_rcf_cost_per_diem", period)
        rcf_capped_per_diem = min_(rcf_per_diem, p.rcf.max_per_diem)
        rcf_cost_of_care = rcf_capped_per_diem * p.rcf.days_multiplier
        rcf_total_income = countable_no_disregard + ssi_monthly
        rcf_client_participation = max_(
            0, rcf_total_income - p.rcf.personal_needs_allowance
        )
        rcf_amt = max_(0, rcf_cost_of_care - rcf_client_participation)
        # IHHRC — IAC 441—177.10(2)(a) and 177.10(3):
        #   payment = max(0, min(cost, per-person cap) − client participation).
        # Client participation = combined marital-unit countable income
        # (without the SSI $20 disregard, per GL 6-B-46 p. 36) minus the
        # applicable FBR. When both spouses need care, split evenly across the
        # marital unit so SPM-unit aggregation does not double-count.
        # Home-maintenance, dependent-diversion, and medical-need deductions
        # are not modeled.
        ihhrc_cost = person("ia_ssa_ihhrc_cost_of_care", period)
        both_need_care = person("ia_ssa_ihhrc_both_need_care", period)
        joint_claim = person("ssi_claim_is_joint", period.this_year)
        basic_ssi_disregard = where(joint_claim, couple_fbr, individual_fbr)
        combined_countable = person.marital_unit.sum(countable_no_disregard)
        combined_participation = max_(0, combined_countable - basic_ssi_disregard)
        ihhrc_client_participation = where(
            both_need_care,
            combined_participation / person.marital_unit.nb_persons(),
            combined_participation,
        )
        ihhrc_eligible_cost = min_(ihhrc_cost, p.ihhrc.max_cost_single)
        ihhrc_amt = max_(0, ihhrc_eligible_cost - ihhrc_client_participation)
        # SMME — IAC 441—52.1(7): flat amount ($1 since 2017).
        smme_amt = p.smme.amount
        return select(
            [
                arrangement == arr_values.RCF,
                arrangement == arr_values.IHHRC,
                arrangement == arr_values.FLH,
                arrangement == arr_values.DP,
                arrangement == arr_values.BLIND,
                arrangement == arr_values.SMME,
            ],
            [rcf_amt, ihhrc_amt, flh_amt, dp_amt, blind_amt, smme_amt],
            default=0,
        )
