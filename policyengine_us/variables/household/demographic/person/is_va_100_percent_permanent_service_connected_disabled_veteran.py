from policyengine_us.model_api import *


class is_va_100_percent_permanent_service_connected_disabled_veteran(Variable):
    """Exact VA and service-status fact used by Maine's additional credit.

    The person served on active duty in the U.S. Armed Forces and, if
    discharged, retired or separated, left under conditions other than
    dishonorable. The VA has actually assigned a rating at 100% for one or
    more service-connected disabilities rated permanent.

    A lower rating paid at 100% through individual unemployability, a
    temporary 100% rating, or a non-service-connected permanent disability
    pension does not establish this fact. No VA cash payment is required.
    Record the actual VA and service determination rather than inferring it
    from the broader disability, veteran or payment inputs. The false default
    is a model assumption, not evidence about an unanswered applicant.
    """

    value_type = bool
    entity = Person
    definition_period = YEAR
    default_value = False
    label = "Veteran with a VA permanent service-connected disability rating of 100%"
    reference = (
        "https://legislature.maine.gov/statutes/36/title36sec5219-KK.html",
        "https://legislature.maine.gov/statutes/36/title36sec653.html",
        # PDF pages 2-3.
        "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/25_1040me_sch_ptfc_fillable.pdf#page=2",
    )
