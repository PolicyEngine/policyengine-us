from policyengine_us.model_api import *


class federal_benefit_cost(Variable):
    value_type = float
    entity = Person
    label = "Federal benefit cost attributed to this person"
    documentation = (
        "Sum of the federal-government portion of benefit expenditures for "
        "programs this person is enrolled in. Grows as programs gain "
        "federal/state attribution — currently Medicaid and CHIP."
    )
    unit = USD
    definition_period = YEAR
    adds = ["medicaid_federal_cost", "chip_federal_cost"]
