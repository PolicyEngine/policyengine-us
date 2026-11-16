from policyengine_us.model_api import *


class ca_cvrp_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Income used for California CVRP direct eligibility"
    documentation = (
        "SPM unit income for California CVRP direct eligibility. The model retains its "
        "existing approximation pending a separate review of program income rules."
    )
    reference = "https://cleanvehiclerebate.org/sites/default/files/docs/nav/transportation/cvrp/documents/CVRP-Implementation-Manual.pdf#page=12"

    adds = "gov.states.ca.calepa.carb.cvrp.income.sources"
