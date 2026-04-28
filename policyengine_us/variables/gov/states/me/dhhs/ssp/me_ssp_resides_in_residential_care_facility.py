from policyengine_us.model_api import *


class me_ssp_resides_in_residential_care_facility(Variable):
    value_type = bool
    entity = Person
    label = "Resides in a Maine Residential Care Facility"
    definition_period = MONTH
    defined_for = StateCode.ME
    default_value = False
    reference = (
        "https://www.maine.gov/sos/sites/maine.gov.sos/files/inline-files/144c332-2025-101%20%28AMD%29_0.docx",
        "https://www.maine.gov/sos/sites/maine.gov.sos/files/content/assets/144c332-appendices-charts.docx",
    )
