from policyengine_us.model_api import *


class or_liheap_income_band(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Oregon LIHEAP payment income band"
    defined_for = StateCode.OR
    reference = (
        "https://www.oregon.gov/ohcs/energy-weatherization/Documents/PY25%20EA%20Operations%20%20Policy%20Manual-%20FINAL%209-27-24.pdf#page=58",
        "https://www.oregon.gov/ohcs/energy-weatherization/Documents/2026%20Final%20Energy%20Assistance%20Intake%20Operations%20%26%20Policy%20Manual.pdf#page=78",
        "https://www.oregon.gov/ohcs/energy-weatherization/Documents/2026%20Final%20Energy%20Assistance%20Intake%20Operations%20%26%20Policy%20Manual.pdf#page=79",
        "https://www.oregon.gov/ohcs/energy-weatherization/Documents/manuals/09-23-2027-PY-2027-EA-Operations-Policy-Manual.pdf#page=72",
        "https://www.oregon.gov/ohcs/energy-weatherization/Documents/manuals/09-23-2027-PY-2027-EA-Operations-Policy-Manual.pdf#page=73",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states["or"].ohcs.liheap.payment
        size = clip(spm_unit("spm_unit_size", period), 1, p.max_household_size)
        income = spm_unit("or_liheap_countable_income", period)
        # Keep the printed inclusive tops, including their $1 irregularities.
        return (
            1
            + (income > p.income_band["1"][size])
            + (income > p.income_band["2"][size])
            + (income > p.income_band["3"][size])
        )
