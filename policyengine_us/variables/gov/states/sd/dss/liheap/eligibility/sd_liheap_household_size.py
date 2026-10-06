from policyengine_us.model_api import *


class sd_liheap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "South Dakota LIEAP household size"
    defined_for = StateCode.SD
    # Physical page 9: "Only citizens and eligible aliens are counted as actual HH
    # members"; page 18: ineligible aliens "are not included in the household
    # count".
    reference = "https://liheapch.acf.gov/sites/default/files/webfiles/docs/SD_Policy-and-Procedures-Manual2018.pdf#page=9"
    adds = ["is_citizen_or_legal_immigrant"]
