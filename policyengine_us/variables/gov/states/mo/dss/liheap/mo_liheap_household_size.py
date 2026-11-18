from policyengine_us.model_api import *


class mo_liheap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Missouri LIHEAP household size"
    documentation = "Number of SPM unit members who are U.S. citizens or qualified noncitizens. Missouri counts citizens and legal permanent residents, and the 2025 manual (page 44) also accepts refugees, asylees, parolees and COFA citizens as qualified noncitizens; other members are left out of the household count but their income counts (mo_liheap_countable_income_person). The SPM unit approximates the household living in private quarters that purchases residential heat in common; roomers, boarders and live-in attendants have no inputs and are not excluded."
    reference = (
        # PDF pages 2-3
        "https://web.archive.org/web/20250603190025/https://www.sos.mo.gov/cmsimages/adrules/csr/current/13csr/13c40-19.pdf#page=2",
        # PDF pages 40-44
        "https://dss.mo.gov/sites/mydss/files/media/pdf/2025/10/liheap-policy-procedure-manual.pdf#page=40",
    )
    defined_for = StateCode.MO

    adds = ["is_citizen_or_legal_immigrant"]
