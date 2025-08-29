from policyengine_us.model_api import *


class id_2022_rebate_floor(Variable):
    value_type = float
    entity = Person
    label = "Idaho 2022 rebate floor"
    definition_period = YEAR
    defined_for = StateCode.ID

    adds = ["gov.states.id.tax.income.credits.2022_rebate.floor"]
