from policyengine_us.model_api import *


class co_ptc_elected(Variable):
    """Whether the claimant elected the Property Tax/Rent/Heat Rebate.

    A PTC election prevents a Disability Assistance Credit in the same tax year.
    Assign a married PTC claim once to the tax unit representing its claimants;
    this input does not calculate a PTC award or infer an optimal election.
    """

    value_type = bool
    entity = TaxUnit
    label = "Colorado Property Tax/Rent/Heat Rebate elected"
    definition_period = YEAR
    default_value = False
    defined_for = StateCode.CO
    reference = (
        "https://leg.colorado.gov/laws/session-laws/HB24-1268/475/download#page=8"
    )
