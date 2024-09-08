from policyengine_us.model_api import *


class ut_personal_exemption_additional_dependents(Variable):
    value_type = int
    entity = TaxUnit
    label = "Utah total additional dependents under the personal exemption"
    definition_period = YEAR
    reference = "https://le.utah.gov/~2023/bills/static/HB0054.html#59-10-1044"  # 59-10-1018 (1)(g)
    defined_for = StateCode.UT
    adds = ["ut_personal_exemption_additional_dependent_eligible"]
