from policyengine_us.model_api import *


class hi_employee_temporary_disability_insurance_contribution(Variable):
    value_type = float
    entity = Person
    label = "Hawaii employee temporary disability insurance contribution"
    documentation = (
        "Employee-side Hawaii temporary disability insurance contribution at "
        "the statutory limit. HRS 392-43(a) lets an employer withhold half the "
        "cost of coverage, up to the employee rate times weekly wages, and "
        "makes the employer pay the balance. Coverage cost varies by employer "
        "and the model holds no premium data, so this assumes the employer "
        "withholds the full rate limit."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.HI
    reference = (
        "https://data.capitol.hawaii.gov/hrscurrent/Vol07_Ch0346-0398/HRS0392/HRS_0392-0043.htm",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.hi.tax.payroll.temporary_disability_insurance
        taxable_wages = person(
            "hi_temporary_disability_insurance_taxable_wages", period
        )
        return p.employee_rate * taxable_wages
