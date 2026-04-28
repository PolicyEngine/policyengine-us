from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.me.dhhs.ssp.me_ssp_living_arrangement import (
    MESSPCategory,
)


class me_ssp_payment_category(Variable):
    value_type = Enum
    entity = Person
    label = "Maine SSP payment category"
    definition_period = MONTH
    defined_for = StateCode.ME
    possible_values = MESSPCategory
    default_value = MESSPCategory.LIVING_ALONE_OR_WITH_OTHERS
    reference = (
        "https://www.maine.gov/sos/sites/maine.gov.sos/files/inline-files/144c332-2025-101%20%28AMD%29_0.docx",
        "https://www.maine.gov/sos/sites/maine.gov.sos/files/content/assets/144c332-appendices-charts.docx",
    )

    def formula(person, period, parameters):
        federal_arrangement = person("ssi_federal_living_arrangement", period.this_year)
        in_medical_facility = (
            federal_arrangement
            == federal_arrangement.possible_values.MEDICAL_TREATMENT_FACILITY
        )
        living_arrangement = person("me_ssp_living_arrangement", period)
        return where(
            in_medical_facility,
            MESSPCategory.MEDICAID_FACILITY,
            living_arrangement,
        )
