from policyengine_us.model_api import *


class CTTFARegion(Enum):
    REGION_A = "Region A"
    REGION_B = "Region B"
    REGION_C = "Region C"


class ct_tfa_region(Variable):
    value_type = Enum
    entity = Household
    possible_values = CTTFARegion
    default_value = CTTFARegion.REGION_B
    definition_period = MONTH
    defined_for = StateCode.CT
    label = "Connecticut TFA payment region"
    reference = (
        "https://portal.ct.gov/dss/-/media/departments-and-agencies/dss/state-plans-and-federal-reports/tanf-state-plan/ct-tanf-plan-2021-2023--draft.pdf#page=56",
        "https://secure.ssa.gov/poms.nsf/lnx/0500830403BOS",
    )
    # NOTE: The official regulation defines regions by city/town,
    # not county. PolicyEngine does not have a town-level input
    # variable, so this remains a user-input enum.
    # See CT TANF State Plan 2021-2023, pp. 56-57 for full
    # town-to-region mapping.
