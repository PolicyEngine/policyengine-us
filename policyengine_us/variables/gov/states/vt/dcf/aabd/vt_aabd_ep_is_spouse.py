from policyengine_us.model_api import *


class vt_aabd_ep_is_spouse(Variable):
    value_type = bool
    entity = Person
    label = "Vermont AABD recipient's Essential Person is an ineligible spouse"
    definition_period = MONTH
    # PDF pages 38, 44
    reference = "https://outside.vermont.gov/dept/DCF/Shared%20Documents/ESD/Rules/2700-AABD.pdf#page=38"
    documentation = "Set on the aged, blind or disabled recipient. Defaults to true when the recipient's marital unit includes a spouse who is not aged, blind or disabled; override when a nonspouse is the essential person."

    def formula(person, period, parameters):
        abd = person("is_ssi_aged_blind_disabled", period.this_year)
        # A marital unit has at most two members, so a non-ABD member of an
        # ABD person's marital unit is that person's spouse.
        return abd & person.marital_unit.any(~abd)
