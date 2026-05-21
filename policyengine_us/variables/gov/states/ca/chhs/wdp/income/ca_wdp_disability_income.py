from policyengine_us.model_api import *


class ca_wdp_disability_income(Variable):
    value_type = float
    entity = Person
    label = "California 250 Percent Working Disabled Program disability income"
    unit = USD
    definition_period = YEAR
    reference = "https://my.dpss.lacounty.gov/public/en/home/epolicy/program/medi-cal/non-magi/250-percent-wdp.html"
    defined_for = StateCode.CA

    adds = "gov.states.ca.chhs.wdp.eligibility.income.sources.disability"
