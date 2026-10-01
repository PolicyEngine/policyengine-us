from policyengine_us.model_api import *


class years_since_us_entry(Variable):
    value_type = float
    entity = Person
    label = "Years since US entry or qualified immigration status grant"
    documentation = (
        "Years since the person entered the United States or was granted the "
        "qualifying immigration status, measured as each program starts its "
        "clock. The federal five-year bar under 8 USC 1613(a) runs from entry "
        "with qualified-alien status; the refugee cash assistance window runs "
        "from entry for refugees and from the status grant for some other "
        "statuses, such as asylees. When not supplied this defaults to 0, so a "
        "noncitizen in a status subject to the five-year bar is treated as "
        "inside the bar, and a refugee as inside the refugee cash assistance "
        "window."
    )
    unit = "year"
    definition_period = YEAR
    # No explicit default_value: the float default of 0 applies. Supply this
    # input to model a person past the five-year bar or outside the refugee
    # cash assistance window. Statuses exempt from the bar are handled through
    # separate parameter lists rather than this clock.
    reference = "https://www.law.cornell.edu/uscode/text/8/1613"
