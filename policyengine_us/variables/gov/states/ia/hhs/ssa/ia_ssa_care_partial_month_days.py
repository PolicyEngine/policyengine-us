from policyengine_us.model_api import *


class ia_ssa_care_partial_month_days(Variable):
    value_type = int
    entity = Person
    label = "Iowa SSA covered care days in a partial month"
    definition_period = MONTH
    defined_for = StateCode.IA
    default_value = 0
    documentation = "Covered days in a month that is not fully covered. For residential care, count the day of entry but not the day of discharge or death, plus authorized reserve bed days; for in-home health-related care, count the days of approved services. Leave at 0 for a full month; a value of at least the month's length is also a full month. Key the entry to its month (for example 2026-01: 15)."
    reference = (
        # 441 IAC 52.1(3)"b", "e" and "f"
        "https://www.legis.iowa.gov/docs/iac/chapter/441.52.pdf#page=2",
        # PDF pages 42, 71-72
        "https://hhs.iowa.gov/media/3987/download?inline=#page=42",
    )

    def formula(person, period, parameters):
        # A formula stops a one-month input from carrying into later months.
        return 0
