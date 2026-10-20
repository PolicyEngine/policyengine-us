from policyengine_us.model_api import *


class ia_ssa_ihhrc_initial_partial_month(Variable):
    value_type = bool
    entity = Person
    label = "Iowa IHHRC initial partial month without client participation"
    definition_period = MONTH
    defined_for = StateCode.IA
    default_value = False
    documentation = "Set only for a first month of in-home health-related care service that is less than a full month, when no client participation is required. Key the entry to its month and enter the covered days in ia_ssa_care_partial_month_days."
    reference = (
        "https://hhs.iowa.gov/media/3987/download?inline=#page=42",
        # 441 IAC 177.8(2)"b"
        "https://www.legis.iowa.gov/docs/iac/chapter/441.177.pdf#page=4",
    )

    def formula(person, period, parameters):
        # A formula stops a one-month input from carrying into later months.
        return False
