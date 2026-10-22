from policyengine_us.model_api import *


class nh_ssp_essential_person_resources(Variable):
    value_type = float
    entity = Person
    label = "New Hampshire SSP essential-person countable resources"
    definition_period = MONTH
    unit = USD
    quantity_type = STOCK
    reference = "https://gc.nh.gov/rules/state_agencies/he-w600.html"
    documentation = "Countable resources of the certified co-resident essential person under adult cash-assistance rules. Enter once, or the same amount on both applicant spouses."
