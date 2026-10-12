from policyengine_us.model_api import *


class nm_ccap_non_traditional_hours(Variable):
    value_type = float
    entity = Person
    unit = "hour"
    definition_period = MONTH
    label = "New Mexico CCAP weekly non-traditional hours of care"
    defined_for = StateCode.NM
    reference = "https://www.nmececd.org/wp-content/uploads/2024/05/Cost-Model-Reimbursement-Rate-Flyer-English-and-Spanish-Revised-May-2024.pdf#page=5"
