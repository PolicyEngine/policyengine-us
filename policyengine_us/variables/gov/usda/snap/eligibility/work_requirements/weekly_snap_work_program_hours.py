from policyengine_us.model_api import *


class weekly_snap_work_program_hours(Variable):
    value_type = float
    entity = Person
    label = "average weekly hours of participation in a SNAP qualifying work program"
    unit = "hour"
    documentation = (
        "Average weekly hours of participation in and compliance with a "
        "work program qualifying under the SNAP ABAWD work requirement, "
        "such as a SNAP Employment and Training program, a program under "
        "the Workforce Innovation and Opportunity Act, or a program under "
        "section 236 of the Trade Act of 1974 (7 U.S.C. 2015(o)(1)(B); "
        "7 CFR 273.24(a)(3)). These hours count toward the 20-hour weekly "
        "ABAWD work-activity threshold, alone or combined with hours of "
        "employment (7 CFR 273.24(a)(1)(i)-(iii)). Survey data does not "
        "capture this input, so it defaults to zero; see "
        "PolicyEngine/populace#249 for the companion data issue."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/7/2015#o_2",
        "https://www.law.cornell.edu/cfr/text/7/273.24#a_1",
    )
