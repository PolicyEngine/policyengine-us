#!/usr/bin/env python3

from policyengine_us.model_api import *


class has_substance_use_disorder(Variable):
    # criteria not yet defined by CMS, so treating as simple boolean for now
    value_type = bool
    entity = Person
    label = "Substance Use Disorder as a measure of medically frail"
    definition_period = YEAR
    reference = "https://www.congress.gov/bill/119th-congress/house-bill/1/text"
    default_value = False
