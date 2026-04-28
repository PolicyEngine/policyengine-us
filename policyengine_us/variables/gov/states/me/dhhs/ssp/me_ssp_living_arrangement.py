from policyengine_us.model_api import *


class MESSPLivingArrangement(Enum):
    LIVING_ALONE_OR_WITH_OTHERS = "Living alone or with others"
    HOUSEHOLD_OF_ANOTHER = "Household of another"
    ADULT_FOSTER_HOME = "Adult Foster Home"
    FLAT_RATE_BOARDING_HOME = "Flat Rate Boarding Home"
    ADULT_FAMILY_CARE_HOME = "Adult Family Care Home"
    COST_REIMBURSED_BOARDING_HOME = "Cost Reimbursed Boarding Home"
    MEDICAID_FACILITY = "Medicaid facility (Title XIX)"
    RESIDENTIAL_CARE_FACILITY = "Residential Care Facility"
    NONE = "None"


class me_ssp_living_arrangement(Variable):
    value_type = Enum
    entity = Person
    label = "Maine SSP living arrangement"
    definition_period = MONTH
    defined_for = StateCode.ME
    possible_values = MESSPLivingArrangement
    default_value = MESSPLivingArrangement.LIVING_ALONE_OR_WITH_OTHERS
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
        in_residential_care = person(
            "me_ssp_resides_in_residential_care_facility", period
        )
        in_cost_reimbursed_boarding = person(
            "me_ssp_resides_in_cost_reimbursed_boarding_home", period
        )
        in_adult_family_care = person(
            "me_ssp_resides_in_adult_family_care_home", period
        )
        in_flat_rate_boarding = person(
            "me_ssp_resides_in_flat_rate_boarding_home", period
        )
        in_adult_foster = person("me_ssp_resides_in_adult_foster_home", period)
        in_household_of_another = person(
            "me_ssp_resides_in_household_of_another", period
        )
        return select(
            [
                in_medical_facility,
                in_residential_care,
                in_cost_reimbursed_boarding,
                in_adult_family_care,
                in_flat_rate_boarding,
                in_adult_foster,
                in_household_of_another,
            ],
            [
                MESSPLivingArrangement.MEDICAID_FACILITY,
                MESSPLivingArrangement.RESIDENTIAL_CARE_FACILITY,
                MESSPLivingArrangement.COST_REIMBURSED_BOARDING_HOME,
                MESSPLivingArrangement.ADULT_FAMILY_CARE_HOME,
                MESSPLivingArrangement.FLAT_RATE_BOARDING_HOME,
                MESSPLivingArrangement.ADULT_FOSTER_HOME,
                MESSPLivingArrangement.HOUSEHOLD_OF_ANOTHER,
            ],
            default=MESSPLivingArrangement.LIVING_ALONE_OR_WITH_OTHERS,
        )
