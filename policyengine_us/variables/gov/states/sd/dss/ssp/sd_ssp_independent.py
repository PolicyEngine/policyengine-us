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
        other_income = sum(
            max_(person(name, period), 0)
            for name in list(source.earned) + list(source.unearned)
        )
        joint = person("ssi_claim_is_joint", period.this_year)
        other_income = where(joint, person.marital_unit.sum(other_income), other_income)
        arrangement = person("ssi_federal_living_arrangement", period)
        la = arrangement.possible_values
        independent = (arrangement == la.OWN_HOUSEHOLD) | (
            arrangement == la.ANOTHER_PERSONS_HOUSEHOLD
        )
        student = person("is_full_time_student", period.this_year) | person(
            "is_part_time_college_student", period.this_year
        )
        eligible = (
            (person("ssi", period) > 0)
            & (other_income == 0)
            & independent
            & (person("age", period.this_year) >= p.minimum_age)
            & ~student
            & ~person("sd_ssp_care_certified", period)
        )
        first = person.marital_unit.reference_entity.members_position == 0
        amount = where(
            joint,
            where(first, p.couple_first_amount, p.couple_second_amount),
            p.individual_amount,
        )
        return eligible * amount
