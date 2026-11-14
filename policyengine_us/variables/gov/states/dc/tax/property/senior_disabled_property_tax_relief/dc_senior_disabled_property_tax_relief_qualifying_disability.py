from policyengine_us.model_api import *


class dc_senior_disabled_property_tax_relief_qualifying_disability(Variable):
    """Whether the individual satisfies DC's specified disability criterion.

    Requires SSA determination of permanent and total disability, or receipt of
    the SSI, SSDI, railroad retirement disability, federal government disability
    or District government disability payments specified in section 47-863.
    Generic disability and private employer disability payments alone do not
    establish this fact. False still permits independent qualification by age.
    """

    value_type = bool
    entity = Person
    label = "DC senior disabled property tax relief qualifying disability"
    definition_period = YEAR
    default_value = False
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/47-863",
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/ASD%20100%20Instructions.pdf#page=1",
    )
