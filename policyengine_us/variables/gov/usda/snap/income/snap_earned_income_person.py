from policyengine_us.model_api import *


class snap_earned_income_person(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "SNAP earned income per person"
    reference = "https://www.law.cornell.edu/cfr/text/7/273.9#b_1"
    unit = USD
    defined_for = "snap_countable_earner"

    adds = "gov.usda.snap.income.sources.earned"
