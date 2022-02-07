from openfisca_us.model_api import *


class is_ca_cvrp_normal_rebate_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Eligible for CVRP normal rebate"
    documentation = "Eligible for California Clean Vehicle Rebate Project (CVRP) normal rebate"
    reference = "https://cleanvehiclerebate.org/en/eligibility-guidelines"

    def formula(person, period, parameters):
        # AGI must be less than the threshold.
        agi = person.tax_unit("c00100", period)
        mars = person.tax_unit("mars", period)
        caps = parameters(period).states.ca.calepa.carb.cvrp.income_cap
        return agi <= caps[mars]
