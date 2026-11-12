from policyengine_us.model_api import *


class liheap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "LIHEAP regular payments"
    documentation = (
        "Each state's regular LIHEAP heating and cooling payment. Leaves out "
        "Michigan's Home Heating Credit, which counts as a refundable state "
        "tax credit, and crisis, weatherization and equipment assistance. Not "
        "yet counted in household benefits or net income."
    )
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/42/8624#b_1_A"
    adds = "gov.hhs.liheap.regular_payments"
