from policyengine_us.model_api import *


class medicare_part_b_premiums(Variable):
    value_type = float
    entity = Person
    label = "Medicare Part B premiums"
    definition_period = YEAR
    unit = USD
    uprating = "calibration.gov.hhs.cms.moop_per_capita"
