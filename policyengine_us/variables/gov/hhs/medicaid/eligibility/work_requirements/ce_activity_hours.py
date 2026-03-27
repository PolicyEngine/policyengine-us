#!/usr/bin/env python3

from policyengine_us.model_api import *


class ce_activity_hours(Variable):
    # criteria not yet defined by CMS, so treating as simple boolean for now
    value_type = float
    entity = Person
    label = "The sum of all hours spent working, doing commmunity service or in a job-training program in the specific month"
    definition_period = MONTH
    reference = "https://www.congress.gov/bill/119th-congress/house-bill/1/text"
    default_value = 0
