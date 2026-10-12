from policyengine_us.model_api import *


class vt_aabd_ep(Variable):
    value_type = float
    entity = Person
    label = "Vermont state-administered Essential Person grant"
    definition_period = MONTH
    unit = USD
    reference = "https://outside.vermont.gov/dept/DCF/Shared%20Documents/ESD/Rules/2700-AABD.pdf"
    defined_for = StateCode.VT

    def formula(person, period, parameters):
        p = parameters(period).gov.states.vt.dcf.aabd
        level = person("vt_aabd_ep_level", period)
        arrangement = person("vt_aabd_living_arrangement", period)
        la = arrangement.possible_values
        independent = arrangement == la.INDEPENDENT
        other = arrangement == la.HOUSEHOLD_OF_ANOTHER
        spouse = person("vt_aabd_ep_is_spouse", period)
        abd = person("is_ssi_aged_blind_disabled", period.this_year)
        participants = abd & (level != level.possible_values.NONE)
        count = person.marital_unit.sum(participants)
        couple = count > 1
        federal = parameters(period).gov.ssa.ssi
        # Both 2026 geographic schedules have the same amounts. Derive the
        # partial levels from rule 2784 and round the standard to cents.
        maximum = where(
            other,
            p.ep.another_household_maximum,
            where(couple, p.ep.couple_maximum, p.ep.individual_maximum),
        )
        base = where(
            couple,
            federal.amount.couple + p.amount.couple.INDEPENDENT,
            where(
                other,
                federal.amount.individual
                * (1 - federal.amount.one_third_reduction_rate)
                + p.amount.individual.HOUSEHOLD_OF_ANOTHER,
                federal.amount.individual + p.amount.individual.INDEPENDENT,
            ),
        )
        standard = np.round(base + p.ep.rate[level] * (maximum - base), 2)
        valid_level = (level != level.possible_values.NONE) & ~(
            spouse & (level == level.possible_values.PARTIAL_34)
        )
        immigration = person("immigration_status", period.this_year)
        immigrant = (immigration == immigration.possible_values.CITIZEN) | person(
            "is_ssi_qualified_noncitizen", period.this_year
        )
        eligible = (
            valid_level
            & abd
            & immigrant
            & (independent | (other & spouse & ~couple))
            & person("vt_aabd_ep_resources_eligible", period)
            & ~person("is_incarcerated", period)
            & person("takes_up_ssi_if_eligible", period)
        )
        amount = max_(standard - person("vt_aabd_ep_countable_income", period), 0)
        grant = np.floor(amount * clip(person("vt_aabd_ep_proration", period), 0, 1))
        return eligible * grant / max_(count, 1)
