from policyengine_us.model_api import *


class pa_liheap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Pennsylvania LIHEAP household size"
    defined_for = StateCode.PA
    reference = (
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dhs/documents/services/assistance/documents/heating-assistance_liheap/2026-liheap-state-plan.pdf#page=40",
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dhs/documents/services/assistance/documents/heating-assistance_liheap/2027-liheap-state-plan.pdf#page=37",
    )

    # Nonqualified members' income counts in full, but they do not increase size.
    # SPM membership approximates the energy economic unit, including related
    # roomers. It cannot identify all prior-recipient, temporary-resident,
    # institutional, or custody exceptions in sections 601.31 and 601.41.
    adds = ["is_citizen_or_legal_immigrant"]
