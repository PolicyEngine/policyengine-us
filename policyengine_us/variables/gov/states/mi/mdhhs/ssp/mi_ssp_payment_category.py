from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.mi.mdhhs.ssp.mi_ssp_living_arrangement import (
    MISSPLivingArrangement,
)


class mi_ssp_payment_category(Variable):
    value_type = Enum
    entity = Person
    label = "Michigan SSP payment category"
    definition_period = MONTH
    defined_for = StateCode.MI
    possible_values = MISSPLivingArrangement
    default_value = MISSPLivingArrangement.INDEPENDENT_LIVING
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/EX/BP/Public/BEM/660.pdf#page=1",
        "https://mdhhs-pres-prod.michigan.gov/olmweb/EX/BP/Public/BEM/660.pdf#page=4",
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/RF/Public/RFT/248.pdf#page=2",
        "https://www.ecfr.gov/current/title-20/section-416.1131",
    )

    def formula(person, period, parameters):
        # Federal living-arrangement codes (20 CFR 416.1131-1133, 416.414)
        # override the manual input for the categories Michigan shares with
        # federal SSI. Adult Foster Care and Home for the Aged categories
        # are MI-specific and fall back to the user-provided input.
        federal_arrangement = person("ssi_federal_living_arrangement", period.this_year)
        federal_values = federal_arrangement.possible_values
        in_medical_facility = (
            federal_arrangement == federal_values.MEDICAL_TREATMENT_FACILITY
        )
        in_another_household = (
            federal_arrangement == federal_values.ANOTHER_PERSONS_HOUSEHOLD
        )
        living_arrangement = person("mi_ssp_living_arrangement", period)
        return select(
            [in_medical_facility, in_another_household],
            [
                MISSPLivingArrangement.INSTITUTION,
                MISSPLivingArrangement.HOUSEHOLD_OF_ANOTHER,
            ],
            default=living_arrangement,
        )
