from policyengine_us.model_api import *


class is_fl_sr_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Income-eligible for the Florida School Readiness program"
    definition_period = MONTH
    defined_for = StateCode.FL
    reference = (
        "https://www.elclc.org/wp-content/uploads/2025/10/2025-2026-Sliding-Fee-Schedule-for-10012025-4-and-6-Percent.pdf#page=2",
        "https://flrules.elaws.us/fac/6m-4.200",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.fl.doe.sr.eligibility.income
        countable_income = spm_unit("fl_sr_countable_income", period)
        monthly_smi = spm_unit("fl_sr_smi", period)
        enrolled = spm_unit("fl_sr_enrolled", period)
        # New applicants enter at 55% SMI; enrolled families remain eligible
        # through 85% SMI at redetermination.
        income_limit = monthly_smi * where(enrolled, p.exit_smi_rate, p.entry_smi_rate)
        return countable_income <= income_limit
