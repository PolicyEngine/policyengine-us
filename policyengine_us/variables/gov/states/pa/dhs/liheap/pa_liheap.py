from policyengine_us.model_api import *


class pa_liheap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Pennsylvania LIHEAP regular heating assistance"
    defined_for = "pa_liheap_eligible"
    reference = (
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dhs/documents/services/assistance/documents/heating-assistance_liheap/2026-liheap-state-plan.pdf#page=42",
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dhs/documents/services/assistance/documents/heating-assistance_liheap/2027-liheap-state-plan.pdf#page=39",
        "http://services.dpw.state.pa.us/oimpolicymanuals/liheap/assets/docs/2025-2026%20Low-Income%20Home%20Energy%20Assistance%20Program%20%28LIHEAP%29.pdf#page=1",
    )
    # Public tables stop at size 11. For larger households, this includes only
    # supported components; their full award remains unverified, not a legal
    # denial. Blended fuel and prior-receipt facts also remain input limitations.
    adds = ["pa_liheap_matrix_amount", "pa_liheap_supplement"]
