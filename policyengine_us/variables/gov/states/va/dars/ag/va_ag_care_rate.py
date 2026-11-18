from policyengine_us.model_api import *


class va_ag_care_rate(Variable):
    value_type = float
    entity = Person
    label = "Virginia Auxiliary Grant approved monthly care rate"
    definition_period = MONTH
    unit = USD
    reference = "https://www.dss.virginia.gov/media/vdss/licensing/documents/assisted-living-facilities/additional-resources/ARC2026_ag_rate_letter.pdf"

    def formula(person, period, parameters):
        maximum = person("va_ag_maximum_care_rate", period)
        facility_rate = person("va_ag_facility_rate", period)
        return where(facility_rate > 0, min_(facility_rate, maximum), maximum)
