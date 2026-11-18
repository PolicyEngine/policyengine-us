from policyengine_us.model_api import *


class wi_cts_tribal_area_i(Variable):
    value_type = bool
    entity = Household
    label = "Wisconsin CTS tribal household in Area I"
    definition_period = MONTH
    defined_for = StateCode.WI
    reference = "https://www.dhs.wisconsin.gov/publications/p23131-25-01.pdf#page=63"
    documentation = "True for an Oneida Tribe household outside the listed Area I counties, which Handbook 5.2.3 places in Area I. Winnebago Tribe households on tax-free land in La Crosse or Marathon counties already use Area I through the county list."
