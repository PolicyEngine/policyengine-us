from policyengine_us.model_api import *


class wi_cts_child_excluded(Variable):
    value_type = bool
    entity = Person
    label = "Wisconsin CTS child excluded by a nonfinancial condition"
    definition_period = MONTH
    reference = "https://www.dhs.wisconsin.gov/publications/p23131-25-01.pdf"
