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
        # Maine adopts the federal SSI living-arrangement codes (Part 11),
        # so federally-classified arrangements override the manual input.
        federal_arrangement = person("ssi_federal_living_arrangement", period.this_year)
        federal_values = federal_arrangement.possible_values
        in_medical_facility = (
            federal_arrangement == federal_values.MEDICAL_TREATMENT_FACILITY
        )
        in_another_household = (
            federal_arrangement == federal_values.ANOTHER_PERSONS_HOUSEHOLD
        )
        living_arrangement = person("me_ssp_living_arrangement", period)
        return select(
            [in_medical_facility, in_another_household],
            [MESSPCategory.MEDICAID_FACILITY, MESSPCategory.HOUSEHOLD_OF_ANOTHER],
            default=living_arrangement,
        )
