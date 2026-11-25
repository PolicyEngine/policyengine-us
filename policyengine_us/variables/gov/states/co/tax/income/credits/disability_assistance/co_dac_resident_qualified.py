from policyengine_us.model_api import *


class co_dac_resident_qualified(Variable):
    """Whether the individual has verified resident qualification for the DAC.

    Full-year Colorado residence establishes this element. This input does not
    determine eligibility for a part-year resident; callers must verify that
    question before supplying true. It excludes disability, income and the PTC
    election. An unspecified false value is an unverified fact rather than a
    determination that the individual is legally ineligible.
    """

    value_type = bool
    entity = Person
    label = "Colorado Disability Assistance Credit qualifying resident"
    definition_period = YEAR
    default_value = False
    defined_for = StateCode.CO
    reference = (
        "https://leg.colorado.gov/laws/session-laws/HB24-1268/475/download#page=6",
        "https://tax.colorado.gov/sites/tax/files/documents/DR0104EZ_2025.pdf#page=3",
    )
