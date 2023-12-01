from policyengine_us.model_api import *


class in_tax_add_back(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana tax add back"
    definition_period = YEAR
    documentation = "Add backs for certain taxes deducted from federal Schedules C, C-EZ, E and/or F."
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-1-3.5"  # (a)(2)
    # use federal variables if they are added later
