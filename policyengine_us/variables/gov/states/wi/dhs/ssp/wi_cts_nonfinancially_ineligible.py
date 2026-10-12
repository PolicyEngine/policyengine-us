from policyengine_us.model_api import *


class wi_cts_nonfinancially_ineligible(Variable):
    value_type = bool
    entity = Family
    label = "Wisconsin CTS family fails a procedural requirement"
    definition_period = MONTH
    reference = "https://www.dhs.wisconsin.gov/publications/p23131-25-01.pdf"
    documentation = "Includes unresolved child-support noncooperation without good cause, disqualifying divestment or lump-sum ineligibility, simultaneous W-2 participation, SSI fully recouped, or unverified residence/custody/SSN requirements. Child-specific kinship care or relationship exclusions use wi_cts_child_excluded."
