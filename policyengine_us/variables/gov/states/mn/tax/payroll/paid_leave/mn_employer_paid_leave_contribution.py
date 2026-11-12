from policyengine_us.model_api import *


class mn_employer_paid_leave_contribution(Variable):
    value_type = float
    entity = Person
    label = "Minnesota employer paid leave contribution"
    documentation = (
        "Employer-side Minnesota Paid Leave premium: the premium the employer "
        "owes on the person's taxable wages (Minn. Stat. 268B.14, subd. 1) "
        "less the employee wage deduction (subds. 3 and 5a). That is at "
        "least the employer's minimum, half the premium or for a small "
        "employer a quarter of the full rate, plus any part of the permitted "
        "employee portion the employer does not deduct."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.MN
    reference = "https://www.revisor.mn.gov/statutes/cite/268B.14"

    def formula(person, period, parameters):
        return person("mn_paid_leave_premium", period) - person(
            "mn_employee_paid_leave_contribution", period
        )
