from policyengine_us.model_api import *


class mn_paid_leave_premium(Variable):
    value_type = float
    entity = Person
    label = "Minnesota Paid Leave premium"
    documentation = (
        "Minnesota Paid Leave premium on the person's taxable wages, which "
        "accrues to and is payable by the employer (Minn. Stat. 268B.14, "
        "subd. 1). The employer pays it less the employee wage deduction."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.MN
    reference = "https://www.revisor.mn.gov/statutes/cite/268B.14"

    def formula(person, period, parameters):
        return person("mn_paid_leave_premium_rate", period) * person(
            "mn_paid_leave_taxable_wages", period
        )
