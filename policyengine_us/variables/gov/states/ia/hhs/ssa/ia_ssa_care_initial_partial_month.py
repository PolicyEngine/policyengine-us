from policyengine_us.model_api import *


class ia_ssa_care_initial_partial_month(Variable):
    value_type = bool
    entity = Person
    label = "Iowa SSA first partial month of in-home or residential care"
    definition_period = MONTH
    defined_for = StateCode.IA
    default_value = False
    documentation = "Set for a first month of in-home health-related care service that is less than a full month, or for the month a resident enters a residential care facility after living at home earlier that month. In-home care then requires no client participation. Residential care deducts the SSI benefit rate for one person, or for a couple when a spouse lived in the home. For a married resident, the month also sets the couple budget (ia_ssa_rcf_couple_budget) when either spouse received SSI or both spouses enter that month; later months budget each spouse alone. Key the entry to its month and enter the covered days in ia_ssa_care_partial_month_days."
    reference = (
        # 441 IAC 52.1(3)"a"(6)
        "https://www.legis.iowa.gov/docs/iac/chapter/441.52.pdf#page=2",
        # 441 IAC 177.8(2)"b" (IAC 8/5/26)
        "https://www.legis.iowa.gov/docs/iac/chapter/441.177.pdf#page=4",
        # 441 IAC 177.10(2)"b" (IAC 2/5/25)
        "https://www.legis.iowa.gov/docs/iac/chapter/01-07-2026.441.177.pdf#page=5",
        # PDF pages 42, 60-61, 63-64
        "https://hhs.iowa.gov/media/3987/download?inline=#page=42",
    )

    def formula(person, period, parameters):
        # A formula stops a one-month input from carrying into later months.
        return False
