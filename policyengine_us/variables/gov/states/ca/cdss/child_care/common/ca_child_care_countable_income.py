from policyengine_us.model_api import *


class ca_child_care_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "California child care countable income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.CA
    reference = (
        "https://www.law.cornell.edu/regulations/california/5-CCR-18078"
    )

    adds = "gov.states.ca.cdss.child_care.income.sources"
