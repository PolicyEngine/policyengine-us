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
        tax_unit = person.tax_unit
        p = parameters(period).gov.usda.summer_ebt
        programs = add(tax_unit, period, p.categorical_eligibility)
        meal_plans = add(tax_unit, period, p.meal_eligibility)
        living_conditions = add(
            tax_unit, period, p.living_condition_eligibility
        )

        is_program_eligible = np.any(programs) & (
            person("is_in_k12_school", period)
        )
        is_meal_eligible = np.any(meal_plans)
        is_living_condition_eligible = np.any(living_conditions)
        state = tax_unit.household("state_code_str", period)
        state_eligible = p.state_eligibility[state].astype(bool)

        return state_eligible & (
            is_program_eligible
            | is_meal_eligible
            | is_living_condition_eligible
        )
