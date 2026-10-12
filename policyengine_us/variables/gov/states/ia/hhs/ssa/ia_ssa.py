from policyengine_us.model_api import *


class ia_ssa(Variable):
    value_type = float
    entity = Person
    label = "Iowa State Supplementary Assistance"
    definition_period = MONTH
    unit = USD
    reference = ("https://hhs.iowa.gov/media/3987/download?inline=",)
    defined_for = "ia_ssa_eligible"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ia.hhs.ssa
        federal = parameters(period).gov.ssa.ssi
        category = person("ia_ssa_category", period)
        c = category.possible_values
        federally_paid = person("ia_ssa_federal", period)
        income = person("ia_ssa_care_countable_income", period)
        extra = max_(person("ia_ssa_care_additional_deductions", period), 0)
        days = clip(person("ia_ssa_care_days", period), 0, period.days)
        # RCF income eligibility uses a 31-day ceiling; payment uses the
        # actual covered days billed by the provider.
        rate = min_(max_(person("ia_ssa_rcf_daily_rate", period), 0), p.rcf_daily_limit)
        rcf_participation = max_(income - p.rcf_personal_needs - extra, 0)
        rcf = max_(rate * days - rcf_participation, 0)
        home = category == c.IN_HOME_CARE
        cost = max_(person("ia_ssa_ihhrc_monthly_cost", period), 0)
        within_limit = (cost <= p.ihhrc_cost_limit) & home
        has_spouse = person.marital_unit.nb_persons() == 2
        maintenance = where(
            has_spouse, federal.amount.couple, federal.amount.individual
        )
        deductions = where(has_spouse, person.marital_unit.sum(extra), extra)
        participation = max_(income - maintenance - deductions, 0)
        participation = where(
            person("ia_ssa_ihhrc_initial_partial_month", period), 0, participation
        )
        covered_cost = cost * days / period.days * within_limit
        total_cost = person.marital_unit.sum(covered_cost)
        # Allocate a common household contribution proportionately to the
        # approved costs, preserving the household's total payable benefit.
        ihhrc = (
            max_(total_cost - participation, 0) * covered_cost / max_(total_cost, 1e-9)
        )
        # The additional Department payment is for SSI-only FLH recipients.
        # One $20 general exclusion applies to the eligible couple.
        joint = person("ssi_couple_computation_applies", period)
        sources = federal.income.sources
        other_income = sum(
            max_(person(name, period), 0)
            for name in list(sources.earned) + list(sources.unearned)
        )
        other_income = where(joint, person.marital_unit.sum(other_income), other_income)
        flh = category == c.FAMILY_LIFE_HOME
        recipients = person.marital_unit.sum(flh)
        top_up = (
            (other_income == 0)
            * (person("ssi", period) > 0)
            * federal.income.exclusions.general
            / where(joint, max_(recipients, 1), 1)
        )
        size = person.marital_unit.nb_persons()
        fpg = parameters(period).gov.hhs.fpg
        poverty = (
            fpg.first_person.CONTIGUOUS_US
            + (size - 1) * fpg.additional_person.CONTIGUOUS_US
        ) / MONTHS_IN_YEAR
        smme = (
            person("ia_ssa_smme_coverage_eligible", period)
            & (
                person("ia_ssa_smme_countable_income", period)
                > p.smme_minimum_fpg_rate * poverty
            )
            & (federally_paid == 0)
        )
        state = select(
            [category == c.RESIDENTIAL_CARE, home, flh, category == c.SMME],
            [rcf, ihhrc, top_up, smme * p.smme_amount],
            default=0,
        )
        return federally_paid + state
