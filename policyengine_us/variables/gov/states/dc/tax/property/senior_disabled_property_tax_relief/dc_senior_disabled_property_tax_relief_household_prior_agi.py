from policyengine_us.model_api import *


class dc_senior_disabled_property_tax_relief_household_prior_agi(Variable):
    """Explicit household AGI for the program's legally required reference year.

    At period 2025 enter 2023 federal AGI of all residents of this residence,
    excluding only fair-market tenants under written leases. Include residents
    in other tax or SPM units. Count joint-return AGI once, not once per person.
    Negative AGI is permitted. Do not substitute current earnings or Schedule H
    income. Later periods require their applicable, source-verified income year.
    Set the companion availability input true only when this aggregate is known.
    """

    value_type = float
    entity = Household
    label = "DC senior disabled property tax relief reference-year household AGI"
    unit = USD
    definition_period = YEAR
    default_value = 0
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/47-863",
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/ASD%20100%20Instructions.pdf#page=1",
    )
