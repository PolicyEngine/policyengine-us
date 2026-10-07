from policyengine_us.model_api import *


class NVOssLivingArrangement(Enum):
    INDEPENDENT_LIVING = "Independent living or living in a parental household"
    HOUSEHOLD_OF_ANOTHER = "Living in the household of another"
    DOMICILIARY_CARE = "State-certified domiciliary care"
    NONE = "No Nevada optional supplement"


class nv_oss_living_arrangement(Variable):
    value_type = Enum
    entity = Person
    definition_period = MONTH
    label = "Nevada OSS living arrangement"
    possible_values = NVOssLivingArrangement
    default_value = NVOssLivingArrangement.NONE
    defined_for = StateCode.NV
    reference = (
        "https://secure.ssa.gov/poms.nsf/lnx/0501415300SF",
        "https://secure.ssa.gov/poms.nsf/lnx/0501415058#i",
    )

    def formula(person, period, parameters):
        care = person("nv_oss_care_setting", period)
        settings = care.possible_values
        federal = person("ssi_federal_living_arrangement", period)
        arrangements = federal.possible_values
        excluded = (
            (federal == arrangements.MEDICAL_TREATMENT_FACILITY)
            | (care == settings.UNCERTIFIED_MEDICAL_FACILITY)
            | (care == settings.PUBLIC_EMERGENCY_SHELTER)
            | (
                (care == settings.DOMICILIARY_CARE)
                & person("is_child", period.this_year)
            )
        )
        return select(
            [
                excluded,
                care == settings.DOMICILIARY_CARE,
                federal == arrangements.ANOTHER_PERSONS_HOUSEHOLD,
                (federal == arrangements.OWN_HOUSEHOLD)
                | (federal == arrangements.CHILD_IN_PARENTAL_HOUSEHOLD),
            ],
            [
                NVOssLivingArrangement.NONE,
                NVOssLivingArrangement.DOMICILIARY_CARE,
                NVOssLivingArrangement.HOUSEHOLD_OF_ANOTHER,
                NVOssLivingArrangement.INDEPENDENT_LIVING,
            ],
            default=NVOssLivingArrangement.NONE,
        )
