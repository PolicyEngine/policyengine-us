from policyengine_us.model_api import *


class eitc_ssn_limitation_waived(Variable):
    value_type = bool
    entity = TaxUnit
    label = "EITC computed without the section 32(m) Social Security number limitation"
    documentation = (
        "Whether the EITC variables accept an ITIN or any Social Security "
        "number in place of the Social Security number valid for employment "
        "that 26 U.S.C. 32(m) requires (eitc_identification_accepted). The "
        "federal credit applies 32(m), so this is false. The state credits "
        "that waive 32(m) set it to state_eitc_ssn_limitation_waived in the "
        "branch they read (federal_eitc_tax_unit in "
        "tools/state_eitc_helpers.py). Rules outside the EITC that require a "
        "valid Social Security number, such as the recovery rebate credits, "
        "read meets_eitc_identification_requirements and keep it."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/32#m"
    default_value = False
