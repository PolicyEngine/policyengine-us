from policyengine_us.model_api import *


class wa_pte_wholly_service_connected_disability(Variable):
    value_type = bool
    entity = Person
    label = "Wholly service-connected disability for the Washington senior and disabled persons property tax exemption veteran pathway before 2016"
    documentation = (
        "For taxes levied for collection before 2016, RCW 84.36.381(3)(b) "
        'admitted a veteran with "one hundred percent service-connected '
        'disability as provided in 42 U.S.C. Sec. 423 (d)(1)(A)". PolicyEngine reads '
        "that as a disability meeting the Social Security definition that is "
        "wholly service-connected. The model has no service-connection input "
        "for that definition, so by default is_disabled stands in for it, and "
        "a fully disabled service-connected veteran "
        "(is_fully_disabled_service_connected_veteran) also qualifies. The "
        "proxy over-includes a veteran whose disability is not "
        "service-connected. Set this to override the default. Used only with "
        "is_veteran, and only before collection year 2016."
    )
    definition_period = YEAR
    reference = (
        # 2008 c 6 s 706, RCW 84.36.381(3)(b)
        "https://lawfilesext.leg.wa.gov/biennium/2007-08/Pdf/Bills/Session%20Laws/House/3104-S2.SL.pdf#page=85",
        # RCW 84.36.383(6)
        "https://app.leg.wa.gov/RCW/default.aspx?cite=84.36.383",
    )

    def formula(person, period, parameters):
        return person("is_disabled", period) | person(
            "is_fully_disabled_service_connected_veteran", period
        )
