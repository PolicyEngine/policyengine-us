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
        "without a protective-services case. OCFS added the preventive and "
        "child-only exceptions to 415.3(e)(1) effective November 24, 2021. "
        "Title XX eligibility also requires district authorization under "
        "415.2(b)."
    )
    reference = (
        "https://ocfs.ny.gov/programs/childcare/regulations/415-Child-Care-Services.pdf#page=18",
        "https://dos.ny.gov/system/files/documents/2021/11/112421.pdf#page=15",
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-415.3",
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-415.2",
    )
