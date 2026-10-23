from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ia.hhs.ssa._smme_spouse_income import (
    smme_spouse_income,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)


class ia_ssa_smme_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Iowa SMME countable income for Medicaid coverage group"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.IA
    documentation = "SSI countable income plus any SSI payment, combined for a couple whose SSI couple computation applies. For a disabled person working above the SGA level, whom SSI does not count, the person's own income, including in-kind support and maintenance and any spouse income deemed under SSI's rules, after SSI's exclusions, including the student earned income exclusion. Deductions and financial groups of a Medicaid coverage category that differ from SSI are not modeled."
    reference = (
        # Iowa Code 249.3(4)(g)
        "https://www.legis.iowa.gov/docs/code/249.pdf#page=2",
        # 441 IAC 51.7(6)
        "https://www.legis.iowa.gov/docs/iac/chapter/441.51.pdf#page=2",
        "https://hhs.iowa.gov/media/3987/download?inline=#page=77",
    )

    def formula(person, period, parameters):
        # 6-B Income (SMME): income "is determined according to SSI income
        # criteria". ia_ssa compares it with 120 percent of the poverty
        # guideline as Iowa Code 249.3(4)(g) sets it ("at least"; see the NOTE
        # in ia_ssa). An eligible couple's combined income is compared with the
        # two-person guideline (ia_ssa.yaml Cases 47-49). With an ineligible
        # spouse, SSI countable income includes the income SSI deems from that
        # spouse, and ia_ssa then uses the two-person guideline; when SSI deems
        # nothing, 8-E p.12 says to "Process as a one-person household"
        # (Cases 83-84).
        # NOTE: Group-specific Medicaid budgeting is not modeled.
        income = person("ssi_countable_income", period) + person("ssi", period)
        # SSI counts income only for people it treats as aged, blind or
        # disabled, so ssi_countable_income is 0 for a disabled person working
        # above the SGA level, whom SMME still covers (Iowa Code
        # 249.3(4)(a)(2)). That person's own income gets SSI's income rules
        # instead: the student earned income exclusion (20 CFR
        # 416.1112(c)(3)), in-kind support and maintenance (416.1130, 416.1140)
        # and the general and earned income exclusions (ia_ssa.yaml Cases 77,
        # 87 and 88). As 8-E pp.12-13 do, a spouse's income above the couple
        # rate less the individual rate, or an aged, blind or disabled
        # spouse's income, is added before the exclusions
        # (ia_ssa_smme_spousal_deeming_applies), and ia_ssa then uses the
        # two-person guideline (Cases 82, 90-92 and 94-97).
        # NOTE: Income deemed from a parent is not modeled on this path.
        earned = max_(
            person("ssi_earned_income", period)
            - person("ssi_blind_or_disabled_working_student_exclusion", period),
            0,
        )
        unearned = person("ssi_unearned_income", period) + person(
            "ssi_in_kind_support_and_maintenance", period
        )
        deemed = person("ia_ssa_smme_spousal_deeming_applies", period)
        spouse_earned, spouse_unearned = smme_spouse_income(person, period)
        earned = earned + deemed * spouse_earned
        unearned = unearned + deemed * spouse_unearned
        own_income = (
            _apply_ssi_exclusions(
                earned * MONTHS_IN_YEAR, unearned * MONTHS_IN_YEAR, parameters, period
            )
            / MONTHS_IN_YEAR
        )
        counted_by_ssi = person("is_ssi_aged_blind_disabled", period.this_year)
        income = where(counted_by_ssi, income, own_income)
        joint = person("ssi_couple_computation_applies", period)
        return where(joint, person.marital_unit.sum(income), income)
