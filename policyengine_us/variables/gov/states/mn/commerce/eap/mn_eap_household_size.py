from policyengine_us.model_api import *


class mn_eap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Minnesota EAP household size"
    defined_for = StateCode.MN
    reference = (
        # PDF pages 80-81
        "https://mn.gov/commerce-stat/pdfs/ffy26-eap-policy-manual.pdf#page=80",
        # PDF pages 82-83
        "https://mn.gov/commerce-stat/pdfs/ffy27-eap-policy-manual.pdf#page=82",
        "https://liheapch.acf.gov/docs/2026/state-plans/MN_Plan_2026.pdf#page=9",
    )
    # SPM units approximate the economic unit that buys energy in common.
    # Ineligible non-citizens are not counted, but their income counts in
    # mn_eap_countable_income. Citizenship is approximated by the existing
    # qualified-status flag; SSN and document checks are not modeled.
    adds = ["is_citizen_or_legal_immigrant"]
