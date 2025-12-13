from policyengine_us.model_api import *


class msp(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Medicare Savings Program benefit"
    definition_period = MONTH
    reference = (
        "https://www.medicare.gov/basics/costs/help/medicare-savings-programs",
    )
    defined_for = "msp_eligible"

    adds = ["msp_benefit_value"]
