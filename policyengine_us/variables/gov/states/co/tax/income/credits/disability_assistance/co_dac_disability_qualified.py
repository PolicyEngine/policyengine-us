from policyengine_us.model_api import *


class co_dac_disability_qualified(Variable):
    """Whether the individual meets the DAC's full-year disability criterion.

    Requires an inability to engage in substantial gainful activity due to a
    medically determinable impairment expected to result in death or lasting at
    least twelve continuous months, and disability throughout the income tax
    year sufficient to qualify for full benefits from a bona fide public or
    private plan or source based solely on disability. This input excludes
    residency, income and the PTC election. Generic disability or receipt of
    disability payments alone does not establish all these facts.
    """

    value_type = bool
    entity = Person
    label = "Colorado Disability Assistance Credit qualifying disability"
    definition_period = YEAR
    default_value = False
    defined_for = StateCode.CO
    reference = (
        "https://leg.colorado.gov/laws/session-laws/HB24-1268/475/download#page=6"
    )
