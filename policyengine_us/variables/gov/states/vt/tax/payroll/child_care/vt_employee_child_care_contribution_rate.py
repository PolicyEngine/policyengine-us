from policyengine_us.model_api import *

MONTHS_IN_QUARTER = 3


class vt_employee_child_care_contribution_rate(Variable):
    value_type = float
    entity = Person
    label = "Vermont employee child care contribution rate"
    documentation = (
        "Annual effective rate of the Vermont Child Care Contribution that an "
        "employer may withhold from wages. Collection began July 1, 2024, so "
        "the annual rate averages the rates in effect at the start of each "
        "calendar quarter, assuming wages accrue evenly over the year. Every "
        "rate change so far began a quarter, so this equals the average over "
        "all twelve months."
    )
    definition_period = YEAR
    unit = "/1"
    defined_for = StateCode.VT
    reference = (
        "https://legislature.vermont.gov/statutes/fullchapter/32/246",
        "https://tax.vermont.gov/business/child-care-contribution",
    )

    def formula(person, period, parameters):
        quarter_starts = period.get_subperiods(MONTH)[::MONTHS_IN_QUARTER]
        return sum(
            parameters(quarter_start).gov.states.vt.tax.payroll.child_care.employee_rate
            for quarter_start in quarter_starts
        ) / len(quarter_starts)
