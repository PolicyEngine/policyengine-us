from openfisca_us.model_api import *


class ca_cvrp_increased_rebate(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "CVRP increased rebate"
    unit = USD
    documentation = "Increased rebate for low- and middle-income participants in California's Clean Vehicle Rebate Project (CVRP)"

    def formula(person, period, parameters):
        # Use school meal FPG ratio.
        fpg_ratio = person.spm_unit("school_meal_fpg_ratio", period)
        p = parameters(period).states.ca.calepa.carb.cvrp.increased_rebate
        claims_normal_rebate = person("ca_cvrp_normal_rebate", period) > 0
        income_eligible = fpg_ratio <= p.fpl_limit
        categorically_eligible = np.any(
            [
                person.spm_unit(program, period)
                for program in p.categorical_eligibility
            ],
            axis=0,
        )
        eligible = income_eligible | categorically_eligible
        # Must also claim the normal rebate.
        return (eligible & claims_normal_rebate) * p.amount
