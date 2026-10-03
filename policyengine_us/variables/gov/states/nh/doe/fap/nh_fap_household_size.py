from policyengine_us.model_api import *


class nh_fap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "New Hampshire FAP household size"
    documentation = "Number of citizens and qualified immigrants in the SPM unit. All members' otherwise countable income remains included."
    reference = "https://www.energy.nh.gov/sites/g/files/ehbemt551/files/inline-documents/sonh/fuel-assistance-program-procedures-manual.pdf#page=11, 12, 34, 35, 36"
    defined_for = StateCode.NH

    # SPM composition approximates the shared residence and economic unit.
    # Custody, foster-child, live-in-care-provider and finer immigration rules
    # are not separately observed by the existing household/status inputs.
    adds = ["is_citizen_or_legal_immigrant"]
