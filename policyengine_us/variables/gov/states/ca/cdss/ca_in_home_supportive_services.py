from policyengine_us.model_api import *


class ca_in_home_supportive_services(Variable):
    value_type = float
    entity = Person
    label = "California In-Home Supportive Services"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "https://www.cdss.ca.gov/in-home-supportive-services"
