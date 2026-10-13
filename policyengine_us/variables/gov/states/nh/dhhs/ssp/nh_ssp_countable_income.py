from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.nh.dhhs.ssp._nh_ssp_couple import (
    nh_ssp_spouse,
    spouse_value,
)


class nh_ssp_countable_income(Variable):
    value_type = float
    entity = Person
    label = "New Hampshire adult assistance group countable income"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.NH
    reference = "https://gc.nh.gov/rules/state_agencies/he-w600.html"
    documentation = "Income for the whole assistance group; a couple shares one grant."

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nh.dhhs.ssp
        arrangement = person("nh_ssp_living_arrangement", period)
        independent = arrangement == arrangement.possible_values.INDEPENDENT
        spouse = nh_ssp_spouse(person, period)
        couple = spouse >= 0
        has_essential_person = person("nh_ssp_has_essential_person", period)
        essential = independent & (
            has_essential_person | spouse_value(has_essential_person, spouse, False)
        )
        eligible = person("nh_ssp_eligible", period)
        both_applicants = eligible & spouse_value(eligible, spouse, False)
        earned = max_(person("ssi_earned_income", period), 0)
        expenses = max_(person("nh_ssp_employment_expenses", period), 0)
        # With a nonapplicant spouse, combine earnings before the applicant's
        # category disregard under He-W 654.02(d)-(e).
        combined = couple & ~both_applicants
        earned = where(combined, earned + spouse_value(earned, spouse), earned)
        expenses = where(combined, expenses + spouse_value(expenses, spouse), expenses)
        blind = person("is_blind", period.this_year)
        blind_net = max_(earned - p.earned.blind_flat, 0) * (
            1 - p.earned.disregard_fraction
        )
        remaining = max_(earned - p.earned.aged_disabled_flat, 0)
        aged_disabled_net = max_(
            remaining
            - min_(
                remaining * p.earned.disregard_fraction,
                p.earned.aged_disabled_remainder_disregard_cap,
            )
            - max_(expenses, p.earned.minimum_employment_expenses),
            0,
        )
        net_earned = where(blind, blind_net, aged_disabled_net)
        net_earned = where(
            both_applicants, net_earned + spouse_value(net_earned, spouse), net_earned
        )
        unearned = max_(person("ssi_unearned_income", period), 0) + person(
            "ssi", period
        )
        # Blind children use the parental allocation in He-W 652.03(f)-(g).
        unearned = unearned + person(
            "ssi_unearned_income_deemed_from_ineligible_parent", period
        )
        unearned = unearned + spouse_value(unearned, spouse)
        other = max_(person("nh_ssp_other_income_deductions", period), 0)
        other = other + spouse_value(other, spouse)
        essential_income = max_(
            person("nh_ssp_essential_person_countable_income", period), 0
        )
        unearned = unearned + essential * max_(
            essential_income, spouse_value(essential_income, spouse)
        )
        disregard = where(
            essential & couple,
            p.three_person_disregard,
            where(couple | essential, p.couple_disregard, p.single_disregard),
        )
        return max_(net_earned + unearned - disregard - other, 0)
