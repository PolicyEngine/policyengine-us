from policyengine_us.model_api import *


class or_liheap_region(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Oregon LIHEAP payment region"
    defined_for = StateCode.OR
    reference = (
        "https://www.oregon.gov/ohcs/energy-weatherization/Documents/PY25%20EA%20Operations%20%20Policy%20Manual-%20FINAL%209-27-24.pdf#page=58",
        "https://www.oregon.gov/ohcs/energy-weatherization/Documents/PY25%20EA%20Operations%20%20Policy%20Manual-%20FINAL%209-27-24.pdf#page=59",
        "https://www.oregon.gov/ohcs/energy-weatherization/Documents/2026%20Final%20Energy%20Assistance%20Intake%20Operations%20%26%20Policy%20Manual.pdf#page=78",
        "https://www.oregon.gov/ohcs/energy-weatherization/Documents/2026%20Final%20Energy%20Assistance%20Intake%20Operations%20%26%20Policy%20Manual.pdf#page=80",
        "https://www.oregon.gov/ohcs/energy-weatherization/Documents/manuals/09-23-2027-PY-2027-EA-Operations-Policy-Manual.pdf#page=72",
        "https://www.oregon.gov/ohcs/energy-weatherization/Documents/manuals/09-23-2027-PY-2027-EA-Operations-Policy-Manual.pdf#page=74",
    )
    documentation = (
        "Zero denotes a county reported as UNKNOWN or an out-of-state household. A "
        "missing county input falls back to the state's first county in the enum, "
        "Baker County, which is in Region 2."
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states["or"].ohcs.liheap.payment.regions
        county = spm_unit.household("county_str", period)
        return select(
            [np.isin(county, p.region_1), np.isin(county, p.region_2)],
            [1, 2],
            default=0,
        )
