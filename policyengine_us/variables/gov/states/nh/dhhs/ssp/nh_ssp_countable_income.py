from policyengine_us.model_api import *


class nh_ssp_countable_income(Variable):
    value_type = float
    entity = Person
    label = "New Hampshire adult assistance group countable income"
    definition_period = MONTH
    unit = USD
    reference = "https://gc.nh.gov/rules/state_agencies/he-w600.html"
    documentation = "Income for the whole assistance group; a couple shares one grant."

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nh.dhhs.ssp
        arrangement = person("nh_ssp_living_arrangement", period)
        independent = arrangement == arrangement.possible_values.INDEPENDENT
        couple = independent & (person.marital_unit.sum(independent) == 2)
        essential = independent & person.marital_unit.any(
            person("nh_ssp_has_essential_person", period)
        )
        both_applicants = (
            person.marital_unit.sum(person("nh_ssp_eligible", period)) == 2
        )
        earned = max_(person("ssi_earned_income", period), 0)
        expenses = max_(person("nh_ssp_employment_expenses", period), 0)
        # With a nonapplicant spouse, combine earnings before the applicant's
        # category disregard under He-W 654.02(d)-(e).
        combined = couple & ~both_applicants
        earned = where(combined, person.marital_unit.sum(earned), earned)
        expenses = where(combined, person.marital_unit.sum(expenses), expenses)
        blind = person("is_blind", period.this_year)
        blind_net = max_(earned - p.earned.blind_flat, 0) * (
            1 - p.earned.disregard_fraction
        )
        remaining = max_(earned - p.earned.aged_disabled_flat, 0)
        aged_disabled_net = max_(
            remaining
            - min_(
                remaining * p.earned.disregard_fraction,
                p.earned.aged_disabled_fraction_cap,
            )
            - max_(expenses, p.earned.minimum_employment_expenses),
            0,
        )
        net_earned = where(blind, blind_net, aged_disabled_net)
        net_earned = where(
            couple & both_applicants, person.marital_unit.sum(net_earned), net_earned
        )
        unearned = max_(person("ssi_unearned_income", period), 0) + person(
            "ssi", period
        )
        # Blind children use the parental allocation defined in He-W 641.04.
        unearned = unearned + person(
            "ssi_unearned_income_deemed_from_ineligible_parent", period
        )
        unearned = where(couple, person.marital_unit.sum(unearned), unearned)
        other = max_(person("nh_ssp_other_income_deductions", period), 0)
        other = where(couple, person.marital_unit.sum(other), other)
        unearned = unearned + essential * person.marital_unit.max(
            max_(person("nh_ssp_essential_person_countable_income", period), 0)
        )
        disregard = where(
            essential & couple,
            p.three_person_disregard,
            where(couple | essential, p.couple_disregard, p.single_disregard),
        )
        return max_(net_earned + unearned - disregard - other, 0)
