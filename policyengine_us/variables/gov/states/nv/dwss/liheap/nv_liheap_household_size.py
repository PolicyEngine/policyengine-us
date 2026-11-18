from policyengine_us.model_api import *


class nv_liheap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Nevada LIHEAP household size"
    defined_for = StateCode.NV
    reference = (
        # PDF pages 32-33, 43, 60
        "https://dss.nv.gov/uploadedFiles/dwssnvgov/content/Energy/FY%202026%20EAP%20Manual%2008.2025%20ADA.pdf#page=32",
        # PDF pages 32-33, 43, 60
        "https://www.dss.nv.gov/contentassets/b3bcdb93ea2d4b3f8dc252451a34cbe4/2027-eap-state-manual--08.25.26-1.pdf#page=32",
    )

    # Citizens and qualified non-citizens who are not within the Section
    # 302 C five-year bar count in household size. Ineligible non-citizens,
    # including those within the bar, are excluded from size, but their
    # income still counts in nv_liheap_countable_income, under the same rules
    # as other members. SPM membership approximates the household; Social
    # Security number noncompliance, program violation disqualifications,
    # students living away, joint custody and roomers or boarders have no
    # inputs.
    adds = ["nv_liheap_immigration_eligible"]
