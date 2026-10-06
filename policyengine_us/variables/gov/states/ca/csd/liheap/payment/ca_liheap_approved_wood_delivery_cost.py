from policyengine_us.model_api import *


class ca_liheap_approved_wood_delivery_cost(Variable):
    """Approved ordinary delivery cost for the modeled program year.

    Approval incorporates eligible quantity, wood form, climate, storage, and
    administrative prioritization. The amount precedes the ordinary benefit cap,
    excludes discretionary supplements, and does not replace income or qualified
    adult eligibility. It is not historical annual wood spending. A zero default
    does not establish legal ineligibility or resolve an unknown delivery cost.
    """

    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    default_value = 0
    label = "California LIHEAP approved eligible wood delivery cost"
    defined_for = StateCode.CA
    # Quantity and pricing: page 188; approved vendor payments: pages 363-364.
    reference = "https://www.csd.ca.gov/Shared%20Documents/2026-Final-LIHEAP-State-Plan.pdf#page=188"
