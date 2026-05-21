from policyengine_us.model_api import *


class has_work_requirement(Variable):
    # FIXME Replace with formula based on MAGI and needing financial qualifications
    value_type = bool
    entity = Person
    label = "Required to do the Medicaid work requirement"
    definition_period = MONTH
    reference = "https://www.congress.gov/bill/119th-congress/house-bill/1/text"
    default_value: False
