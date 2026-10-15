from policyengine_us.model_api import *


class vt_aabd_ep_is_spouse(Variable):
    value_type = bool
    entity = Person
    label = "Vermont AABD recipient's Essential Person is an ineligible spouse"
    definition_period = MONTH
    # PDF pages 38, 44
    reference = "https://outside.vermont.gov/dept/DCF/Shared%20Documents/ESD/Rules/2700-AABD.pdf#page=38"
    documentation = "True for an aged, blind or disabled recipient whose marital unit includes a spouse who is not aged, blind or disabled, unless vt_aabd_ep_nonspouse_essential_person is set."

    def formula(person, period, parameters):
        abd = person("is_ssi_aged_blind_disabled", period.this_year)
        # A marital unit has at most two members, so a non-ABD member of an
        # ABD person's marital unit is that person's spouse.
        return (
            abd
            & person.marital_unit.any(~abd)
            & ~person("vt_aabd_ep_nonspouse_essential_person", period)
        )
