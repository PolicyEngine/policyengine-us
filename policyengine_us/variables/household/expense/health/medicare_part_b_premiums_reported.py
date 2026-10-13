from policyengine_us.model_api import *


class medicare_part_b_premiums_reported(Variable):
    value_type = float
    entity = Person
    label = "Medicare Part B premiums (reported)"
    definition_period = YEAR
    unit = USD
    # Grows with the standard premium: within an income tier, a premium with
    # its income-related adjustment is a fixed multiple of the standard
    # premium before rounding (42 U.S.C. 1395r(i)(3)), though hold-harmless
    # limits and Medicare Advantage premium reductions move some people's
    # premiums differently.
    uprating = "calibration.gov.hhs.cms.medicare_part_b_premium_per_enrollee"
