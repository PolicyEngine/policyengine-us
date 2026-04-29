from policyengine_us.model_api import *


class de_paid_leave_contribution_rate(Variable):
    value_type = float
    entity = Person
    label = "Delaware paid leave contribution rate"
    documentation = "Combined Delaware paid leave contribution rate by employer size."
    definition_period = YEAR
    unit = "/1"
    defined_for = StateCode.DE

    def formula(person, period, parameters):
        p = parameters(period).gov.states.de.tax.payroll.paid_leave
        headcount = person("employer_headcount", period)
        full_coverage_rate = p.family_caregiver_rate + p.medical_rate + p.parental_rate
        return select(
            [
                headcount < p.small_employer_threshold,
                headcount < p.full_coverage_threshold,
            ],
            [0, p.parental_rate],
            default=full_coverage_rate,
        )
