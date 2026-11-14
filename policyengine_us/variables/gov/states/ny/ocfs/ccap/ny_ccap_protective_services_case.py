from policyengine_us.model_api import *


class ny_ccap_protective_services_case(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "New York CCAP protective services case"
    defined_for = StateCode.NY
    documentation = (
        "New York treats an open protective-services case as a family-level "
        "route under 18 NYCRR 415.2(a)(3)(vi). PolicyEngine uses "
        "receives_or_needs_protective_services for that case status. "
        "Preventive child care uses a separate receipt input and Title XX "
        "authorization."
    )
    reference = (
        "https://ocfs.ny.gov/programs/childcare/regulations/415-Child-Care-Services.pdf#page=15",
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-415.2",
    )

    def formula(spm_unit, period, parameters):
        return add(spm_unit, period, ["receives_or_needs_protective_services"]) > 0
