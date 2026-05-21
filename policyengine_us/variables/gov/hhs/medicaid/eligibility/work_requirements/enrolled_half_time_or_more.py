#!/usr/bin/env python3

from policyengine_us.model_api import *


class enrolled_half_time_or_more(Variable):
    # criteria not yet defined by CMS, so treating as simple boolean for now
    value_type = bool
    entity = Person
    label = "The individual is enrolled in an educational program at least half-time."
    definition_period = MONTH
    reference = "https://www.congress.gov/bill/119th-congress/house-bill/1/text"
    default_value = False
