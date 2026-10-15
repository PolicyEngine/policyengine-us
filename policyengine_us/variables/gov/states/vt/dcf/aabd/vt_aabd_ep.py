from policyengine_us.model_api import *


class vt_aabd_ep(Variable):
    value_type = float
    entity = Person
    label = "Vermont state-administered Essential Person grant"
    definition_period = MONTH
    unit = USD
    # PDF pages 36, 43-45, 49-50
    reference = "https://outside.vermont.gov/dept/DCF/Shared%20Documents/ESD/Rules/2700-AABD.pdf#page=36"
    defined_for = StateCode.VT

    def formula(person, period, parameters):
        p = parameters(period).gov.states.vt.dcf.aabd
        federal = parameters(period).gov.ssa.ssi.amount
        level = person("vt_aabd_ep_level", period)
        levels = level.possible_values
        arrangement = person("vt_aabd_living_arrangement", period)
        la = arrangement.possible_values
        independent = arrangement == la.INDEPENDENT
        other = arrangement == la.HOUSEHOLD_OF_ANOTHER
        spouse = person("vt_aabd_ep_is_spouse", period)
        valid_level = (level != levels.NONE) & ~(spouse & (level == levels.PARTIAL_34))
        # vt_aabd_ep_resources_eligible already tests the whole marital unit.
        abd_eligible = (
            person("is_ssi_aged_blind_disabled", period.this_year)
            & (independent | (other & spouse))
            & person("vt_aabd_ep_resources_eligible", period)
            & ~person("is_incarcerated", period)
            & person("takes_up_ssi_if_eligible", period.this_year)
        )
        # Rules 2780(A), 2783.1 and 2784(C): an eligible couple receives one
        # grant for a shared essential person. The rules do not address
        # different levels for each spouse; use the highest level certified for
        # either spouse.
        certified = abd_eligible & valid_level
        person_eligible = abd_eligible & person.marital_unit.any(certified)
        rate = person.marital_unit.max(where(certified, p.ep.rate[level], 0))
        count = person.marital_unit.sum(person_eligible)
        couple = count > 1
        # Rule 2784(B)-(C): the individual maximum is the combined couple
        # payment, the another-household maximum is the combined independent
        # individual payment, and the couple maximum adds an increment to the
        # combined couple payment. Both 2026 geographic schedules have the
        # same amounts.
        couple_combined = federal.couple + p.amount.couple.INDEPENDENT
        individual_combined = federal.individual + p.amount.individual.INDEPENDENT
        maximum = where(
            other,
            individual_combined,
            couple_combined + couple * p.ep.couple_increment,
        )
        base = where(
            couple,
            couple_combined,
            where(
                other,
                federal.individual * (1 - federal.one_third_reduction_rate)
                + p.amount.individual.HOUSEHOLD_OF_ANOTHER,
                individual_combined,
            ),
        )
        # Derive the partial levels from rule 2784(A) and round to cents.
        standard = np.round(base + rate * (maximum - base), 2)
        amount = max_(standard - person("vt_aabd_ep_countable_income", period), 0)
        # NOTE: The rule 2784 application-month proration is not modeled.
        eligible = person_eligible & (independent | ~couple)
        return eligible * np.floor(amount) / max_(count, 1)
