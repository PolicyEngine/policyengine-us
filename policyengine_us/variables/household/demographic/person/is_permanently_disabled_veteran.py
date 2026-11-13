from policyengine_us.model_api import *


class is_permanently_disabled_veteran(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Veteran with a VA permanent and total disability rating"
    documentation = (
        "The Department of Veterans Affairs has rated the veteran's disability "
        "permanent and total, for service-connected compensation or for a "
        "disability pension under 38 U.S.C. 1521(a). North Carolina's military "
        "retirement deduction reads this flag in place of a medical retirement "
        "under 10 U.S.C. chapter 61, which has no input of its own; a chapter "
        "61 retiree without this rating is not covered. Also set 'Veteran with "
        "a VA service-connected disability rated or paid at 100%' "
        "(is_fully_disabled_service_connected_veteran) when the disability is "
        "service-connected and rated or paid at 100%. These flags don't set "
        "is_veteran; enter VA payments as veterans_benefits. Aid-and-attendance "
        "or housebound status alone does not count; enter any total rating the "
        "veteran also holds with these flags."
    )
    reference = (
        "https://www.ecfr.gov/current/title-38/section-3.340#p-3.340(b)",
        "https://www.law.cornell.edu/uscode/text/38/1521#a",
    )
