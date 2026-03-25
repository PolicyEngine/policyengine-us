from policyengine_us.model_api import *


class vt_employer_child_care_contribution(Variable):
    value_type = float
    entity = Person
    label = "Vermont employer child care contribution"
    documentation = (
        "Employer-side Vermont Child Care Contribution, assuming the employer "
        "contributes only the minimum required employer share."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.VT

    def formula(person, period, parameters):
        rate = parameters(period).gov.states.vt.tax.payroll.child_care.employer_rate
        return rate * person("payroll_tax_gross_wages", period)
