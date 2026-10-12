from policyengine_us.model_api import *


class ca_wdp_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = (
        "California 250 Percent Working Disabled Program immigration status eligible"
    )
    definition_period = YEAR
    documentation = (
        "Whether this person meets the SSI/SSP immigration-status screen for "
        "California's 250% Working Disabled Program. This is narrower than "
        "California's broader full-scope Medi-Cal immigration rules."
    )
    reference = (
        "https://stgenssa.sccgov.org/debs/program_handbooks/medi-cal/assets/26250WDP/ElgCriteria.htm",
    )
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        qualified_noncitizen = person("is_ssi_qualified_noncitizen", period)
        immigration_status = person("immigration_status", period)
        citizen = immigration_status == immigration_status.possible_values.CITIZEN
        return citizen | qualified_noncitizen
