from policyengine_us.model_api import *


class snap_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "SNAP earned income"
    documentation = (
        "Earned income for calculating the SNAP earned income deduction"
    )
    reference = "https://www.law.cornell.edu/cfr/text/7/273.9#b_1"
    unit = USD

    adds = "gov.usda.snap.income.sources.earned"
