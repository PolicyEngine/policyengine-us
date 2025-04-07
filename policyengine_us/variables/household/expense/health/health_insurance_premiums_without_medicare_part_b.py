from policyengine_us.model_api import *


class health_insurance_premiums_without_medicare_part_b(Variable):
    value_type = float
    entity = Person
    label = "Health insurance premiums without Medicare Part B premiums"
    unit = USD
    definition_period = YEAR
    uprating = "calibration.gov.hhs.cms.moop_per_capita"
