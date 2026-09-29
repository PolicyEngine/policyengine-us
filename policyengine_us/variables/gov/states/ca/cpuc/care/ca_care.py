from policyengine_us.model_api import *


class ca_care(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    unit = USD
    label = "California CARE"
    documentation = (
        "California's CARE program discounts electricity and natural gas bills "
        "for eligible households. Only customers of utilities the California "
        "Public Utilities Commission regulates can enroll; municipal utilities "
        "such as the Los Angeles Department of Water and Power and Riverside "
        "Public Utilities run their own programs. The model has no "
        "utility-territory input, so it applies CARE to every eligible "
        "California household."
    )
    reference = "https://www.cpuc.ca.gov/industries-and-topics/electrical-energy/electric-costs/care-fera-program"
    defined_for = "ca_care_eligible"
    adds = ["ca_care_electricity", "ca_care_gas"]
