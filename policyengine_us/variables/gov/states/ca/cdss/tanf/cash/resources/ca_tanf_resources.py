from policyengine_us.model_api import *


class ca_tanf_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "California CalWORKs Resources"
    unit = USD
    definition_period = YEAR
    quantity_type = STOCK
    defined_for = StateCode.CA
    reference = "https://my.dpss.lacounty.gov/public/en/home/epolicy/program/calworks/property/property.html"

    adds = "gov.states.ca.cdss.tanf.cash.resources.sources"
