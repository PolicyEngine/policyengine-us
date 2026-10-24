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
        # PDF pages 44-46
        "https://www.cdss.ca.gov/Portals/9/CAPI/CAPI_Regulations-Accessible.pdf#page=44",
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=12200",
    )

    def formula(person, period, parameters):
        individual, couple = ca_capi_ssi_ssp_standard(person, period, parameters)
        p = parameters(period).gov.states.ca.cdss.capi.payment_standard_offset
        joint = person("ssi_couple_computation_applies", period)
        # Each member of a couple takes half the couple standard less half the
        # couple offset, so a couple with one SSI/SSP member is one half-offset
        # below the SSI/SSP couple standard (MPP 49-050.12-.13).
        return where(joint, (couple - p.couple) / 2, individual - p.single)
