from policyengine_us.model_api import *


class ny_ccap_protective_services_case(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "New York CCAP open protective or preventive services case"
    defined_for = StateCode.NY
    documentation = (
        "18 NYCRR 415.2(a)(2)(vi)(b) attaches the protective and preventive "
        "services route to the family rather than to the individual child, so "
        "one flagged member qualifies the whole unit. The preventive-services "
        "half of the rule is not separately modeled because PolicyEngine has "
        "no preventive-services variable."
    )
    reference = "https://ocfs.ny.gov/programs/childcare/regulations/415-Child-Care-Services.pdf#page=15"

    def formula(spm_unit, period, parameters):
        return add(spm_unit, period, ["receives_or_needs_protective_services"]) > 0
