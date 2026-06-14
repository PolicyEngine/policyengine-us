from policyengine_us.model_api import *


class ca_scc_general_assistance_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = (
        "Eligible for Santa Clara County General Assistance based on immigration status"
    )
    defined_for = "in_scc"
    reference = "https://stgenssa.sccgov.org/debs/program_handbooks/general_assistance/assets/07Citizens_Noncitizens/Non_Citizen_Status.htm"

    def formula(person, period, parameters):
        # GA 141 limits eligibility to noncitizens with the right to remain
        # permanently or indefinitely. The handbook excludes parolees admitted
        # "for a specific period of time" — only indefinite-period parolees
        # qualify, so PAROLED_ONE_YEAR (a fixed-term admission) is excluded
        # from the qualified status list.
        p = parameters(period).gov.local.ca.scc.general_assistance
        immigration_status = person("immigration_status", period.this_year)
        immigration_status_str = immigration_status.decode_to_str()
        return np.isin(immigration_status_str, p.qualified_immigration_status)
