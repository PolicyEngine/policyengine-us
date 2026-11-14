from policyengine_us.model_api import *


class dc_senior_disabled_property_tax_relief_ownership_share(Variable):
    """Individual's qualifying legal share of this residence, from zero to one.

    Enter the person's own supported legal interest in the same eligible home or
    cooperative dwelling. Do not repeat a combined couple share on both people,
    combine shares to satisfy the individual's threshold, or substitute a Medicaid
    equity share. Zero represents no established qualifying ownership interest.
    """

    value_type = float
    entity = Person
    label = "DC senior disabled property tax relief individual ownership share"
    unit = "/1"
    definition_period = YEAR
    default_value = 0
    reference = "https://code.dccouncil.gov/us/dc/council/code/sections/47-863"
