from policyengine_us.model_api import *


class va_ag_care_rate(Variable):
    value_type = float
    entity = Person
    label = "Virginia Auxiliary Grant approved monthly care rate"
    definition_period = MONTH
    unit = USD
    reference = "https://www.dss.virginia.gov/media/vdss/licensing/documents/assisted-living-facilities/additional-resources/ARC2026_ag_rate_letter.pdf"
    documentation = "Defaults to the published locality maximum. Use the approved provider rate when it is below that maximum."

    def formula(person, period, parameters):
        return person("va_ag_maximum_care_rate", period)
