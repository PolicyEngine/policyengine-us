from policyengine_us.model_api import *


class INSSPLivingArrangement(Enum):
    MEDICAID_FACILITY = "Medicaid-certified health care facility"
    LICENSED_RESIDENTIAL = "Licensed residential care facility"
    UNLICENSED_RESIDENTIAL = "Unlicensed residential care facility"
    NONE = "None"


class in_ssp_living_arrangement(Variable):
    value_type = Enum
    entity = Person
    label = "Indiana SSP living arrangement"
    definition_period = YEAR
    defined_for = StateCode.IN
    possible_values = INSSPLivingArrangement
    default_value = INSSPLivingArrangement.NONE
    reference = (
        "https://secure.ssa.gov/poms.nsf/lnx/0501401001CHI",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/in.html",
    )

    def formula(person, period):
        arrangement = person("ssi_federal_living_arrangement", period)
        in_medical_facility = (
            arrangement == arrangement.possible_values.MEDICAL_TREATMENT_FACILITY
        )

        in_licensed = person("in_resides_in_licensed_residential_facility", period)
        in_unlicensed = person("in_resides_in_unlicensed_residential_facility", period)

        return select(
            [in_medical_facility, in_licensed, in_unlicensed],
            [
                INSSPLivingArrangement.MEDICAID_FACILITY,
                INSSPLivingArrangement.LICENSED_RESIDENTIAL,
                INSSPLivingArrangement.UNLICENSED_RESIDENTIAL,
            ],
            default=INSSPLivingArrangement.NONE,
        )
