#!/usr/bin/env python3

from policyengine_us.model_api import *


class has_serious_or_complex_medical_condition(Variable):
    # criteria not yet defined by CMS, so treating as simple boolean for now
    value_type = bool
    entity = Person
    label = "Has a serious or complex medical condition"
    definition_period = YEAR
    reference = "https://www.congress.gov/bill/119th-congress/house-bill/1/text"
    default_value = False

