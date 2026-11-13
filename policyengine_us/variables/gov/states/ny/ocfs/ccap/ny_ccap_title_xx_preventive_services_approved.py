from policyengine_us.model_api import *


class ny_ccap_title_xx_preventive_services_approved(Variable):
    value_type = bool
    entity = Person
    label = "District authorizes New York Title XX preventive child care"
    definition_period = MONTH
    set_input = set_input_dispatch_by_period
    default_value = False
    defined_for = StateCode.NY
    documentation = (
        "Records district authorization for this child's preventive child "
        "care under Title XX during the month. The district must fund the "
        "service, include eligible families in its plan and apply applicable "
        "need, priority and financial conditions. Authorization also records "
        "satisfaction of the provider and any required OCFS approval "
        "conditions under 18 NYCRR 415.1 and 415.2(b). PolicyEngine applies "
        "the 415.1(b) age test separately; the completed authorization covers "
        "every other applicable state and federal eligibility condition for "
        "this child, provider and month. For a child who turned 13 during "
        "the school year, authorization records that the school-year "
        "continuation still runs. Set this input to false when authorization "
        "ends, including at the end of that continuation."
    )
    reference = (
        "https://ocfs.ny.gov/programs/childcare/regulations/415-Child-Care-Services.pdf",
        "https://ocfs.ny.gov/programs/childcare/regulations/404-Eligibility.pdf",
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-415.1",
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-415.2",
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-404.5",
    )
