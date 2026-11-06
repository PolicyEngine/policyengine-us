from policyengine_us.model_api import *


class dc_employer_paid_leave_tax_rate(Variable):
    value_type = float
    entity = Person
    label = "District of Columbia employer paid leave tax rate"
    documentation = (
        "Annual effective rate of the District of Columbia Paid Family Leave "
        "tax. The District changed the rate on April 1, 2019, July 1, 2022 and "
        "July 1, 2024, so the annual rate averages the rate in effect in each "
        "month, assuming wages accrue evenly over the year."
    )
    definition_period = YEAR
    unit = "/1"
    defined_for = StateCode.DC
    reference = "https://dcpaidfamilyleave.dc.gov/employer-information/"

    def formula(person, period, parameters):
        return (
            sum(
                parameters(month).gov.states.dc.tax.payroll.paid_leave.employer_rate
                for month in period.get_subperiods(MONTH)
            )
            / MONTHS_IN_YEAR
        )
