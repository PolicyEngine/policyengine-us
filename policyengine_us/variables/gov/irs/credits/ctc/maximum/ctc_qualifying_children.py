from policyengine_us.model_api import *


class ctc_qualifying_children(Variable):
    value_type = int
    entity = TaxUnit
    label = "CTC-qualifying children"
    documentation = "Count of children that qualify for the Child Tax Credit"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/24#c"

    adds = ["ctc_qualifying_child"]
