from policyengine_us.model_api import *


class oh_has_not_taken_oh_lump_sum_credits(Variable):
    value_type = bool
    entity = Person
    label = "Ohio flag for having not taken ohio lump sum credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=20",
        "https://codes.ohio.gov/ohio-revised-code/section-5747.055",
    )
    defined_for = StateCode.OH
