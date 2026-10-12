from policyengine_us.model_api import *


class wa_eceap_categorically_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Categorically eligible for Washington ECEAP"
    definition_period = YEAR
    defined_for = StateCode.WA
    reference = (
        "https://app.leg.wa.gov/RCW/default.aspx?cite=43.216.505",
        "https://app.leg.wa.gov/WAC/default.aspx?cite=110-425-0080",
    )

    def formula(person, period, parameters):
        # Homeless and IEP are the two modelable categorical paths under
        # RCW 43.216.505(4). Foster care is NOT a categorical path here —
        # it appears in the priority/preference language for slot allocation
        # among eligible children, and as a risk factor under RCW 43.216.512.
        is_homeless = person.household("is_homeless", period)
        has_iep = person("has_individualized_education_program", period)
        return is_homeless | has_iep
