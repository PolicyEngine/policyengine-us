from policyengine_us.model_api import *


class is_summer_ebt_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Summer EBT"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1762#h_2"
        "https://www.fns.usda.gov/summer/sunbucks",
        "https://www.joinproviders.com/summer-ebt/",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.usda.summer_ebt
        programs = add(person.spm_unit, period, p.categorical_eligibility)
        meal_plans = add(person.spm_unit, period, p.meal_eligibility)
        living_conditions = add(
            person.spm_unit, period, p.living_condition_eligibility
        )
        is_program_eligible = (
            np.any([person.spm_unit(program, period) for program in programs])
            | person("medicaid", period)
        ) & (person("is_in_k12_school", period))
        is_meal_eligible = np.any(
            [person.spm_unit(program, period) for program in programs]
        )
        is_living_condition_eligible = np.any(
            [person.spm_unit(program, period) for program in programs]
        )
        state_eligible = p.state_eligibility[state].astype(bool)
        return state_eligible & (
            is_program_eligible
            | is_meal_eligible
            | is_living_condition_eligible
        )
