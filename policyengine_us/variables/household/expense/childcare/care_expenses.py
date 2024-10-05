from policyengine_us.model_api import *


class care_expenses(Variable):
    value_type = float
    entity = Person
    label = "Care expenses"
    unit = USD
    definition_period = MONTH

    def formula(person, period, parameters):
        return person("pre_subsidy_care_expenses", period)

    # Add subsidies in a .yaml file once added to the model
