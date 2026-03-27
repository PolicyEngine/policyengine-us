#!/usr/bin/env python3

from policyengine_us.model_api import *


class ce_activity_income(Variable):
    # Letting this be set for now, might later derive it
    value_type = float
    entity = Person
    label = "The sum of all income earned during the month that can be counted toward work requirements"  
    definition_period = MONTH
    reference = "https://www.congress.gov/bill/119th-congress/house-bill/1/text"
    default_value = 0
