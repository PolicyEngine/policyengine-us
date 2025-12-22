from policyengine_us.model_api import *


class ne_child_care_subsidy_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Nebraska Child Care Subsidy countable income"
    unit = USD
    definition_period = YEAR
    reference = "https://dhhs.ne.gov/Guidance%20Docs/Title%20392%20-%20Child%20Care%20Subsidy.pdf"
    defined_for = StateCode.NE

    adds = "gov.states.ne.dhhs.child_care_subsidy.income.countable_sources"
