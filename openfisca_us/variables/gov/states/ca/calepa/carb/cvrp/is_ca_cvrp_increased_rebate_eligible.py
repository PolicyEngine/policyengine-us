from policyengine_us.model_api import *


class is_ca_cvrp_increased_rebate_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Eligible for CVRP increased rebate"
    documentation = "Eligible for increased rebate for low- and middle-income participants in California's Clean Vehicle Rebate Project (CVRP)"
    reference = "https://cleanvehiclerebate.org/en/eligibility-guidelines"
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        # Use school meal FPG ratio.
        spm_unit = person.spm_unit
        fpg_ratio = spm_unit("school_meal_fpg_ratio", period)
        p = parameters(period).gov.states.ca.calepa.carb.cvrp.increased_rebate
        income_eligible = fpg_ratio <= p.fpl_limit
        categorically_eligible = (
            aggr(spm_unit, period, p.categorical_eligibility) > 0
        )
        return income_eligible | categorically_eligible
