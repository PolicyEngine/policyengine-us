from policyengine_us.model_api import *


class dc_senior_disabled_property_tax_relief_household_prior_agi_available(Variable):
    """Whether the full household's required reference-year AGI is known.

    True certifies that the companion aggregate uses the correct residents,
    reference year and fair-market-written-lease tenant exclusion. This separates
    known zero income from missing data. False suppresses an estimate and does
    not establish that the household is legally ineligible.
    """

    value_type = bool
    entity = Household
    label = "DC senior disabled property tax relief reference-year AGI available"
    definition_period = YEAR
    default_value = False
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/47-863",
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/ASD%20100%20Instructions.pdf#page=1",
    )
