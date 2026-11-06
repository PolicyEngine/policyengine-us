from policyengine_us.model_api import *

MONTHS_IN_QUARTER = 3


class dc_employer_paid_leave_tax_rate(Variable):
    value_type = float
    entity = Person
    label = "District of Columbia employer paid leave tax rate"
    documentation = (
        "Annual effective rate of the District of Columbia Paid Family Leave "
        "tax. Employers pay this tax by calendar quarter, and each rate change "
        "so far began a quarter, so the annual rate averages the four quarterly "
        "rates, assuming wages accrue evenly over the year."
    )
    definition_period = YEAR
    unit = "/1"
    defined_for = StateCode.DC
    reference = (
        "https://dcpaidfamilyleave.dc.gov/employer-information/",
        "https://does.dc.gov/sites/default/files/dc/sites/does/publication/attachments/Employment%20Services%20Department%20of%20%207%20DCMR%20%20Ch.%2034%20%20Paid%20Leave%20Contributions.pdf#page=6",
    )

    def formula(person, period, parameters):
        quarter_starts = period.get_subperiods(MONTH)[::MONTHS_IN_QUARTER]
        return sum(
            parameters(month).gov.states.dc.tax.payroll.paid_leave.employer_rate
            for month in quarter_starts
        ) / len(quarter_starts)
