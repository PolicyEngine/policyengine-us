from policyengine_us.model_api import *


class NYSSPCareSetting(Enum):
    FAMILY_CARE = "New York certified family care (congregate care level I)"
    RESIDENTIAL_CARE = "New York certified residential care (congregate care level II)"
    ENHANCED_RESIDENTIAL_CARE = (
        "New York certified enhanced residential care (congregate care level III)"
    )
    DEVELOPMENTAL_OR_MENTAL_HEALTH_FACILITY = (
        "OPWDD intermediate care facility or OMH hospital"
    )
    EXCLUDED = "Setting excluded from the New York State Supplement Program"
    NONE = "No certified care or designated facility setting"


class ny_ssp_care_setting(Variable):
    value_type = Enum
    entity = Person
    label = "New York SSP care setting"
    definition_period = MONTH
    defined_for = StateCode.NY
    possible_values = NYSSPCareSetting
    default_value = NYSSPCareSetting.NONE
    reference = (
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-398-4.5",
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-398-3.4",
    )
    documentation = """
    Certified care levels require an operating certificate for the facility.
    Family and residential care for minors require the authorized placements
    in 18 NYCRR 398-4.5. DEVELOPMENTAL_OR_MENTAL_HEALTH_FACILITY covers OPWDD
    intermediate care facilities and OMH hospitals, which pay the lower
    personal needs allowance when Medicaid pays most of the cost of care.
    EXCLUDED covers publicly operated residences, emergency shelters and other
    medical facilities, such as general hospitals, that the State Supplement
    Program does not pay. Use separate marital units for a spouse living apart
    in an excluded setting, and for couples after their month of entry into an
    institutional level II or III facility.
    """
