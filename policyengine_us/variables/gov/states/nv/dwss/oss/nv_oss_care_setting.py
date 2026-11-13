from policyengine_us.model_api import *


class NVOssCareSetting(Enum):
    DOMICILIARY_CARE = "State-certified domiciliary care"
    UNCERTIFIED_MEDICAL_FACILITY = (
        "Private medical facility not certified under Medicaid"
    )
    PUBLIC_EMERGENCY_SHELTER = "Public emergency shelter for the full month"
    NONE = "No special Nevada supplementation care setting"


class nv_oss_care_setting(Variable):
    value_type = Enum
    entity = Person
    definition_period = MONTH
    label = "Nevada OSS care setting"
    possible_values = NVOssCareSetting
    default_value = NVOssCareSetting.NONE
    reference = "https://secure.ssa.gov/poms.nsf/lnx/0501415300SF"
    documentation = """
    Domiciliary care means a private nonmedical facility, or a public
    nonmedical institution serving at most 16 people, licensed or authorized
    by Nevada to provide personal care to unrelated adults. The uncertified
    medical setting means a private facility not certified under Medicaid.
    The public emergency shelter setting applies to residence throughout
    the month. Other SSI medical-facility inputs continue to apply.
    """
