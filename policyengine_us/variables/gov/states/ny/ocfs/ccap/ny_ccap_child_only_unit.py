from policyengine_us.model_api import *


class ny_ccap_child_only_unit(Variable):
    value_type = bool
    entity = SPMUnit
    label = "New York CCAP child care services unit contains only eligible children"
    definition_period = MONTH
    set_input = set_input_dispatch_by_period
    default_value = False
    defined_for = StateCode.NY
    documentation = (
        "Records a child care services unit containing only eligible children "
        "under 18 NYCRR 415.1(l)(1)(iv). The children live only with people "
        "outside their parent, step-parent, adoptive parent or financially "
        "responsible legal guardian relationships. Tax-unit roles cannot "
        "identify those legal relationships. Apply this status only when no "
        "adult family member receives public assistance. OCFS added the "
        "child-only exception to the 415.3(e)(1) family share effective "
        "November 24, 2021."
    )
    reference = (
        "https://ocfs.ny.gov/programs/childcare/regulations/415-Child-Care-Services.pdf",
        "https://dos.ny.gov/system/files/documents/2021/11/112421.pdf#page=15",
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-415.1",
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-415.3",
    )
