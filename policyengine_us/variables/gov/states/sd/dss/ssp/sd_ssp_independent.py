from policyengine_us.model_api import *


class sd_ssp_independent(Variable):
    value_type = float
    entity = Person
    label = "South Dakota independent living state supplement"
    definition_period = MONTH
    unit = USD
    reference = "https://sdlegislature.gov/Rules/Administrative/67:12:14"
    defined_for = StateCode.SD

    def formula(person, period, parameters):
        p = parameters(period).gov.states.sd.dss.ssp
        source = parameters(period).gov.ssa.ssi.income.sources
        floored_sources = [
            max_(person(name, period), 0)
            for name in list(source.earned) + list(source.unearned)
        ]
        own_income = sum(floored_sources)
        receives_ssi = (person("ssi", period) > 0) | person("receives_ssi", period)
        arrangement = person("ssi_federal_living_arrangement", period)
        la = arrangement.possible_values
        independent = (arrangement == la.OWN_HOUSEHOLD) | (
            arrangement == la.ANOTHER_PERSONS_HOUSEHOLD
        )
        student = person("is_full_time_student", period.this_year) | person(
            "is_part_time_college_student", period.this_year
        )
        qualifies = (
            receives_ssi
            & independent
            & (person("age", period.this_year) >= p.minimum_age)
            & ~student
            & ~person("sd_ssp_care_certified", period)
        )
        # NOTE: ARSD 67:12:14 and POMS DEN01415.011 B.5 are silent on a
        # married recipient whose spouse does not qualify; that recipient is
        # treated as an individual, with no spousal income pooling.
        couple = person("ssi_claim_is_joint", period.this_year) & (
            person.marital_unit.sum(qualifies) > 1
        )
        other_income = where(couple, person.marital_unit.sum(own_income), own_income)
        first = person.marital_unit.reference_entity.members_position == 0
        amount = where(
            couple,
            where(first, p.couple_first_amount, p.couple_second_amount),
            p.individual_amount,
        )
        return (qualifies & (other_income == 0)) * amount
