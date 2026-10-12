from policyengine_us.model_api import *


class is_snap_workfare_participant(Variable):
    value_type = bool
    entity = Person
    label = "participates in and complies with a SNAP workfare program"
    documentation = (
        "Whether the person participates in and complies with the "
        "requirements of a workfare program under 7 CFR 273.7(m) or a "
        "comparable state or local program. Workfare participation "
        "satisfies the SNAP ABAWD work requirement regardless of the "
        "number of hours, since workfare hours are set by dividing the "
        "household benefit by the minimum wage (7 U.S.C. 2015(o)(2)(C); "
        "7 CFR 273.24(a)(1)(iv)). Survey data does not capture this "
        "input, so it defaults to false; see PolicyEngine/populace#249 "
        "for the companion data issue."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/7/2015#o_2_C",
        "https://www.law.cornell.edu/cfr/text/7/273.24#a_1_iv",
    )
