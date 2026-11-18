from policyengine_us.model_api import *


class me_heap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Maine HEAP household size"
    defined_for = StateCode.ME
    reference = (
        # PDF pages 6, 15
        "https://www.mainehousing.org/docs/default-source/msha-rules/ch24-home-energy-assistance-program-rule.pdf#page=6",
        "https://www.maine.gov/sos/sites/maine.gov.sos/files/inline-files/346c024.docx",
    )

    # Rule 3(A)(1) leaves members who are not citizens, nationals or qualified
    # aliens out of the size, and rule 3(C)(1) still counts their income.
    adds = ["is_citizen_or_legal_immigrant"]
