from policyengine_us.model_api import *


class medicare_part_b_premiums_reported(Variable):
    value_type = float
    entity = Person
    label = "Medicare Part B premiums (reported)"
    definition_period = YEAR
    unit = USD
    # A Part B premium, with any income-related adjustment, is a fixed
    # multiple of the standard premium (42 U.S.C. 1395r(i)(3)).
    uprating = "calibration.gov.hhs.cms.medicare_part_b_premium_per_enrollee"
