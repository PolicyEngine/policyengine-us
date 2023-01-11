from policyengine_us.model_api import *


class snap_deductions(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP income deductions"
    unit = USD
    documentation = "Deductions made from gross income for SNAP benefits"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/7/2014#e"

    adds = "gov.usda.snap.income.deductions.allowed"
