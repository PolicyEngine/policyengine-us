from policyengine_us.model_api import *


class is_permanently_disabled_veteran(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Veteran with a VA permanent and total disability rating"
    documentation = (
        "The Department of Veterans Affairs has rated the veteran's disability "
        "permanent and total, for service-connected compensation or for a "
        "disability pension under 38 U.S.C. 1521(a). Also set "
        "is_fully_disabled_service_connected_veteran when the disability is "
        "service-connected and rated or paid at 100%. A veteran the VA finds in "
        "need of regular aid and attendance or permanently housebound has no "
        "input."
    )
    reference = (
        "https://www.ecfr.gov/current/title-38/section-3.340#p-3.340(b)",
        "https://www.law.cornell.edu/uscode/text/38/1521#a",
    )
