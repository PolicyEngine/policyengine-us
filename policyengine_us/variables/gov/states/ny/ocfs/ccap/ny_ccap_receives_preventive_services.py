from policyengine_us.model_api import *


class ny_ccap_receives_preventive_services(Variable):
    value_type = bool
    entity = Person
    label = "Receives New York CCAP child care as a preventive service"
    definition_period = MONTH
    set_input = set_input_dispatch_by_period
    default_value = False
    defined_for = StateCode.NY
    documentation = (
        "Records that this child receives child care as a preventive service "
        "under 18 NYCRR 415.3(e)(1). Families receive a family-share exemption "
        "without a protective-services case. Title XX eligibility also "
        "requires district authorization under 415.2(b)."
    )
    reference = (
        "https://ocfs.ny.gov/programs/childcare/regulations/415-Child-Care-Services.pdf#page=19",
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-415.3",
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-415.2",
    )
