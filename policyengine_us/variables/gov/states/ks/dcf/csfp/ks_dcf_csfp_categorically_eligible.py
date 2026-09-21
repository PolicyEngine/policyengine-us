from policyengine_us.model_api import *


class ks_dcf_csfp_categorically_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Kansas DCF CSFP categorically income eligible"
    defined_for = StateCode.KS
    reference = (
        "https://www.dcf.ks.gov/services/ees/Documents/Food_Distribution_Programs/CSFPStatePlan.pdf#page=4",
        # 7 CFR 247.9(b)(1) and (b)(3)
        "https://www.law.cornell.edu/cfr/text/7/247.9#b",
    )
    adds = "gov.states.ks.dcf.csfp.categorical_eligibility"
