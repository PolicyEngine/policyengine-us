from policyengine_us.model_api import *


class liheap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "LIHEAP regular payments"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/42/8624#b_1_A"
    adds = "gov.hhs.liheap.regular_payments"
