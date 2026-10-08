from policyengine_us.model_api import *


class ar_liheap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Arkansas LIHEAP household size"
    defined_for = StateCode.AR
    documentation = (
        "Number of citizens and qualified noncitizens in the household. Other "
        "members' otherwise countable income remains included in full. The "
        "FY2025 draft manual's composition rule is corroborated by the current "
        "rights statement of a state-designated LIHEAP subgrantee."
    )
    reference = (
        # Draft manual sections 4.4-4.4.1; not an adopted FY2026 manual.
        # PDF pages 36-37
        "https://liheapch.acf.gov/sites/default/files/webfiles/docs/2025/manuals/AR_Manual%5Bdraft%5D_2025.pdf#page=36",
        # Current operator's rights statement, item 9; no revision date shown.
        "https://www.cscdc.net/rights-responsibilities-of-liheap-applicants/",
        # State designation of CSCDC; revised May 11, 2026.
        "https://adeq.state.ar.us/energy/initiatives/pdfs/LIHEAP-SubgranteeNetworkServiceTerritories.pdf#page=2",
    )
    # Do not import SNAP-specific waiting periods or immigration restrictions.
    # Qualified COFA/battered and other cases absent from immigration_status
    # require an override of the existing qualified-status flag. Identity and
    # immigration-document verification remain administrative assumptions.
    adds = ["is_citizen_or_legal_immigrant"]
