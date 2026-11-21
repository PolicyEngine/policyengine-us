from policyengine_us.model_api import *

MONTHS_IN_QUARTER = 3


class or_employee_statewide_transit_tax_rate(Variable):
    value_type = float
    entity = Person
    label = "Oregon employee statewide transit tax rate"
    documentation = (
        "Annual effective rate of the Oregon statewide transit tax. Employers "
        "began withholding the tax on July 1, 2018, so the annual rate averages "
        "the rates in effect at the start of each calendar quarter, assuming "
        "wages accrue evenly over the year. Every rate change so far began a "
        "quarter, so this equals the average over all twelve months."
    )
    definition_period = YEAR
    unit = "/1"
    defined_for = StateCode.OR
    reference = (
        "https://www.oregonlegislature.gov/bills_laws/ors/ors320.html",
        "https://www.oregon.gov/dor/programs/businesses/pages/statewide-transit-tax.aspx",
    )

    def formula(person, period, parameters):
        quarter_starts = period.get_subperiods(MONTH)[::MONTHS_IN_QUARTER]
        return sum(
            parameters(quarter_start)
            .gov.states["or"]
            .tax.payroll.statewide_transit.employee_rate
            for quarter_start in quarter_starts
        ) / len(quarter_starts)
