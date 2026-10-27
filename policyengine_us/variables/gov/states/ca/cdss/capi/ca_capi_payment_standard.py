from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ca.cdss.capi._ca_capi_ssi_ssp_standard import (
    ca_capi_ssi_ssp_standard,
)


class ca_capi_payment_standard(Variable):
    value_type = float
    entity = Person
    label = "California CAPI payment standard"
    unit = USD
    definition_period = MONTH
    defined_for = "ca_capi_eligible_person"
    reference = (
        # PDF pages 3, 44-47
        "https://www.cdss.ca.gov/Portals/9/CAPI/CAPI_Regulations-Accessible.pdf#page=3",
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=12200",
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=18941",
        "https://secure.ssa.gov/apps10/poms.nsf/lnx/0501415058",
        "https://cdss.ca.gov/Portals/9/Additional-Resources/Letters-and-Notices/ACINs/2025/I-59_25.pdf#page=5",
    )

    def formula(person, period, parameters):
        individual, couple = ca_capi_ssi_ssp_standard(person, period, parameters)
        p = parameters(period).gov.states.ca.cdss.capi.payment_standard_offset
        joint = person("ssi_couple_computation_applies", period)
        capi_members = person.marital_unit.sum(
            person("ca_capi_eligible_person", period.this_year)
        )
        # Each member of a CAPI couple takes one-half (MPP 49-050.12, 49-055.4).
        both_capi = joint & (capi_members > 1)
        # A spouse receiving SSI/SSP counts as an eligible spouse (MPP
        # 49-005(e)(3)), so the CAPI member of a mixed couple takes the whole
        # couple standard (MPP 49-050.13) and ca_capi_person subtracts that
        # spouse's SSI/SSP.
        mixed = joint & ~both_capi
        return select(
            [both_capi, mixed],
            [(couple - p.couple) / 2, couple - p.mixed_couple],
            default=individual - p.single,
        )
