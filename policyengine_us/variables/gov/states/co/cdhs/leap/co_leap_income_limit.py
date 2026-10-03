from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi


class co_leap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Colorado LEAP annual income limit"
    defined_for = StateCode.CO
    reference = (
        "https://drive.google.com/file/d/1G3XKsXyKoPZmsA5-P6NI6w3svP99xOZd/view#page=4"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.co.cdhs.leap.income
        size = spm_unit("co_leap_household_size", period)
        capped_size = min_(size, p.additional_person_threshold)
        state = spm_unit.household("state_code_str", period)
        monthly = np.floor(
            p.smi_rate * smi(capped_size, state, period, parameters) / MONTHS_IN_YEAR
        )
        extra = max_(size - p.additional_person_threshold, 0)
        # Flooring reproduces all eight FY2026 published SMI rows; the
        # independently printed increment governs additional members.
        annual_limit = (monthly + extra * p.additional_person_amount) * MONTHS_IN_YEAR
        return where(size > 0, annual_limit, 0)
