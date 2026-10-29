from policyengine_us.model_api import *


class me_heap_categorically_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Maine HEAP categorical income eligibility"
    defined_for = StateCode.ME
    reference = (
        "https://www.mainehousing.org/docs/default-source/msha-rules/ch24-home-energy-assistance-program-rule.pdf#page=15",
        "https://www.maine.gov/sos/sites/maine.gov.sos/files/inline-files/346c024.docx",
        "https://liheapch.acf.gov/docs/2026/state-plans/ME_Plan_2026.pdf#page=5",
    )

    def formula(spm_unit, period, parameters):
        # Rule 3(C)(2): members on a Maine DHHS TANF or SNAP notice of decision
        # are income eligible. Their benefit is scored on actual income, which
        # 3(C)(2) permits ("using actual vetted income"); the pre-established
        # poverty percentages it also allows are in MaineHousing's HEAP Guide,
        # which was posted and is no longer available.
        return add(spm_unit, period, ["snap", "tanf"]) > 0
