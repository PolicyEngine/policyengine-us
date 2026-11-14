from policyengine_us.model_api import *


class mi_qualified_disabled_veteran(Variable):
    value_type = bool
    entity = Person
    label = "Qualified disabled veteran for the Michigan income tax exemption"
    defined_for = StateCode.MI
    definition_period = YEAR
    reference = (
        "https://www.legislature.mi.gov/Laws/MCL?objectName=mcl-206-30",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2025/MI-1040-Book.pdf#page=10",
        "https://web.archive.org/web/20260218211009/https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2025/MI-1040CR-7-Book.pdf?rev=e4ba4fedc63942e48442037517312d4a&hash=AF396E577B1932DF55BFD7F22D7EF06A#page=7",
    )

    def formula(person, period, parameters):
        # MCL 206.30(3)(b)(i)-(ii): "a veteran with a service-connected
        # disability", which is "a disability incurred or aggravated in the
        # line of duty in the active military, naval, or air service as
        # described in 38 USC 101(16)". The definition names no rating, so a
        # veteran at any rating qualifies, and a veteran with a 100% rating
        # qualifies once.
        # (iii) limits "veteran" to an individual "discharged or released
        # from the individual's service with an honorable or general
        # discharge". The model has no discharge input, so each input below
        # stands for a veteran with an honorable or general discharge.
        any_rating = person("is_service_connected_disabled_veteran", period)
        full_rating = person("is_fully_disabled_service_connected_veteran", period)
        return any_rating | full_rating
