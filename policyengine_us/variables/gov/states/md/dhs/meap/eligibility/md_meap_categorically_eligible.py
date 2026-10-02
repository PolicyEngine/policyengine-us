from policyengine_us.model_api import *


class md_meap_categorically_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Maryland MEAP categorical income eligibility"
    defined_for = StateCode.MD
    reference = (
        # PDF pages 11, 62, 63.
        "https://dhs.maryland.gov/documents/OHEP/OHEP-Operations-Manual.pdf#page=11",
        "https://liheapch.acf.gov/docs/2026/state-plans/MD_Plan_2026.pdf#page=5",
    )
    documentation = "One member's receipt of SNAP, TCA or SSI waives the income test. Means-tested veterans benefits are also legally qualifying, but generic veterans_benefits cannot identify that subset. Recurring receipt in the program year is approximated by annual benefit receipt."

    def formula(spm_unit, period, parameters):
        return add(spm_unit, period, ["snap", "tanf", "ssi"]) > 0
