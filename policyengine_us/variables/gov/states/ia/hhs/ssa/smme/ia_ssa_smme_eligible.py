from policyengine_us.model_api import *


class ia_ssa_smme_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Iowa SSA SMME eligible"
    defined_for = StateCode.IA
    reference = (
        "https://www.legis.iowa.gov/docs/iac/chapter/01-07-2026.441.51.pdf#page=2",
        "https://www.legis.iowa.gov/docs/code/249.3.pdf",
    )

    def formula(person, period, parameters):
        # IAC 441—51.7(6): "Income of a recipient" must exceed 120% of the
        # federal poverty level. The test is on the SSI claimant's own (or
        # joint claim couple's) income, not on a larger SPM unit, so size
        # the FPL by the SSI claim — 1 person for an individual, 2 for a
        # joint claim — rather than by SPM unit size.
        aged_or_disabled = person("is_ssi_aged_blind_disabled", period.this_year)
        has_medicaid = person("ia_ssa_has_full_medicaid", period)
        has_medicare = person("ia_ssa_has_medicare_part_b", period)
        p = parameters(period).gov.states.ia.hhs.ssa
        p_fpg = parameters(period).gov.hhs.fpg
        countable_monthly = (
            person("ssi_countable_income", period.this_year) / MONTHS_IN_YEAR
        )
        state_group = person.household("state_group_str", period.this_year)
        first_person = p_fpg.first_person[state_group]
        additional_person = p_fpg.additional_person[state_group]
        joint_claim = person("ssi_claim_is_joint", period.this_year)
        annual_fpg = first_person + where(joint_claim, additional_person, 0)
        fpg_monthly = annual_fpg / MONTHS_IN_YEAR
        income_above_fpl_floor = (
            countable_monthly > p.smme.minimum_income_fpl_multiplier * fpg_monthly
        )
        return aged_or_disabled & has_medicaid & has_medicare & income_above_fpl_floor
