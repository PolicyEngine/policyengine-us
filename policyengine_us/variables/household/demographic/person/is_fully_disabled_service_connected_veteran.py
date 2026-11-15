from policyengine_us.model_api import *


class is_fully_disabled_service_connected_veteran(Variable):
    value_type = bool
    entity = Person
    label = "Veteran with a VA service-connected disability rated or paid at 100%"
    documentation = (
        "The Department of Veterans Affairs rates or pays a service-connected "
        "disability at the 100% (total) rate, temporary or permanent, "
        "including a total rating based on individual unemployability. Also "
        "set 'Veteran with a VA permanent and total disability rating' "
        "(is_permanently_disabled_veteran) when the VA rates the disability "
        "permanent and total. Leave this false for a rating below 100%, unless "
        "the VA pays at the 100% rate for individual unemployability. These "
        "flags don't set is_veteran; enter VA payments as veterans_benefits."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/38/1114#j",
        "https://www.law.cornell.edu/uscode/text/38/1155",
        "https://www.ecfr.gov/current/title-38/section-3.340#p-3.340(a)(1)",
        "https://www.ecfr.gov/current/title-38/section-4.16#p-4.16(a)",
    )
