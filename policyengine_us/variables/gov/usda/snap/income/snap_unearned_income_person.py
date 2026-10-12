from policyengine_us.model_api import *


class snap_unearned_income_person(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "SNAP unearned income per person"
    reference = "https://www.law.cornell.edu/cfr/text/7/273.9#b_2"
    unit = USD

    adds = "gov.usda.snap.income.sources.unearned"
