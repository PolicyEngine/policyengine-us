from policyengine_us.model_api import *


class IASSALivingArrangement(Enum):
    RCF = "Residential care facility"
    IHHRC = "In-home health-related care"
    FLH = "Family-life home"
    DP = "Dependent person"
    BLIND = "Blind"
    SMME = "Supplement for Medicare and Medicaid eligibles"
    NONE = "Not in an Iowa SSA category"


class ia_ssa_living_arrangement(Variable):
    value_type = Enum
    entity = Person
    definition_period = MONTH
    label = "Iowa SSA living arrangement"
    possible_values = IASSALivingArrangement
    default_value = IASSALivingArrangement.NONE
    defined_for = StateCode.IA
    reference = "https://www.legis.iowa.gov/docs/iac/chapter/01-07-2026.441.52.pdf"

    def formula(person, period, parameters):
        eligible = person("ia_ssa_eligible", period)
        p = parameters(period).gov.states.ia.hhs.ssa
        countable_monthly = (
            person("ssi_countable_income", period.this_year) / MONTHS_IN_YEAR
        )
        ssi_monthly = person("ssi", period.this_year) / MONTHS_IN_YEAR
        countable_no_disregard = person("ia_ssa_countable_income_no_disregard", period)
        p_ssi = parameters(period).gov.ssa.ssi.amount
        individual_fbr = p_ssi.individual
        couple_fbr = p_ssi.couple
        joint_claim = person("ssi_claim_is_joint", period.this_year)
        basic_ssi_disregard = where(joint_claim, couple_fbr, individual_fbr)
        # IAC 441—51.4(3) cross-refs 52.1(3)"a": RCF income eligibility compares
        # client participation (total monthly income minus the personal needs
        # allowance) against 31 × the maximum per diem. GL 6-B-46 p. 54 omits
        # the SSI $20 disregard, so use countable_no_disregard.
        rcf_total_income = countable_no_disregard + ssi_monthly
        rcf_client_participation = max_(
            0, rcf_total_income - p.rcf.personal_needs_allowance
        )
        in_rcf = person("ia_ssa_resides_in_residential_care_facility", period)
        rcf_income_threshold = p.rcf.days_multiplier * p.rcf.max_per_diem
        rcf_income_eligible = rcf_client_participation < rcf_income_threshold
        needs_ihhrc = person("ia_ssa_needs_in_home_health_related_care", period)
        both_need_care = person("ia_ssa_ihhrc_both_need_care", period)
        # IAC 441—177.4(1)(f) caps combined marital-unit countable income at
        # $480.55 (one spouse needs care) or $961.10 (both need care) after
        # the basic SSI standard disregard. GL 6-B-46 p. 36 omits the $20
        # disregard, so use countable_no_disregard.
        combined_countable = person.marital_unit.sum(countable_no_disregard)
        ihhrc_countable_after_disregard = max_(
            0, combined_countable - basic_ssi_disregard
        )
        ihhrc_cap = where(
            both_need_care, p.ihhrc.max_cost_couple, p.ihhrc.max_cost_single
        )
        ihhrc_income_eligible = ihhrc_countable_after_disregard <= ihhrc_cap
        in_flh = person("ia_ssa_resides_in_family_life_home", period)
        # IAC 441—177.4(1)(c): IHHRC recipients must live in their own home,
        # so exclude those residing in an RCF or family-life home.
        in_own_home = ~in_rcf & ~in_flh
        has_dependent = person("ia_ssa_dp_has_eligible_dependent", period)
        dp_configuration = person("ia_ssa_dp_configuration", period)
        in_dp = dp_configuration != dp_configuration.possible_values.NONE
        # IAC 441—52.1(2): DP requires the dependent's countable income below
        # the dependent income limit (per IAC 441—51.5(1)). Gate at the
        # living-arrangement level so people who qualify for DP but fail the
        # dependent-income test fall through to Blind / SMME rather than
        # receiving a zero DP supplement.
        dependent_income = person("ia_ssa_dp_dependent_countable_income", period)
        dependent_income_eligible = dependent_income < p.dp.dependent_income_limit
        is_blind = person("is_blind", period.this_year)
        # IAC 441—52.1(4) blind standard is a federally-administered SSP;
        # supplement phases to zero when countable income reaches FBR + state
        # standard. Mirror that ceiling in the category gate so blind
        # recipients with excess income fall through to the next category.
        blind_income_eligible = countable_monthly < individual_fbr + p.blind
        smme_eligible = person("ia_ssa_smme_eligible", period)
        return select(
            [
                eligible & in_rcf & rcf_income_eligible,
                eligible & needs_ihhrc & in_own_home & ihhrc_income_eligible,
                eligible & in_flh,
                eligible & has_dependent & in_dp & dependent_income_eligible,
                eligible & is_blind & blind_income_eligible,
                eligible & smme_eligible,
            ],
            [
                IASSALivingArrangement.RCF,
                IASSALivingArrangement.IHHRC,
                IASSALivingArrangement.FLH,
                IASSALivingArrangement.DP,
                IASSALivingArrangement.BLIND,
                IASSALivingArrangement.SMME,
            ],
            default=IASSALivingArrangement.NONE,
        )
