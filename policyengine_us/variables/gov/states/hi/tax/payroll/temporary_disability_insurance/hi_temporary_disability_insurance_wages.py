from policyengine_us.model_api import *


class hi_temporary_disability_insurance_wages(Variable):
    value_type = float
    entity = Person
    label = "Hawaii temporary disability insurance wages"
    documentation = (
        "Wages as HRS 392-3 defines them: all remuneration, less the payments "
        "HRS 383-11 lists. That list covers what an employer pays under a plan "
        "for medical expenses or retirement and what it pays to a trust "
        "described in IRC 401(a). HRS 383-11(5) stops at payments made without "
        "a deduction from pay, and paragraphs (1) and (4) carry no such limit, "
        "so salary-reduction amounts for these plans come out. The list names "
        "no dependent care payment, so dependent care benefits stay in. The "
        "federal payroll wage base differs because Congress added rules for "
        "elective deferrals, cafeteria plans and dependent care that Hawaii did "
        "not enact. Before 2015 retirement deferrals stay in, because the "
        "model's elective deferral limit starts in 2015."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.HI
    reference = (
        "https://data.capitol.hawaii.gov/hrscurrent/Vol07_Ch0346-0398/HRS0392/HRS_0392-0003.htm",
        "https://data.capitol.hawaii.gov/hrscurrent/Vol07_Ch0346-0398/HRS0383/HRS_0383-0011.htm",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.hi.tax.payroll.temporary_disability_insurance
        remuneration = person("employment_income", period)
        excluded = add(person, period, p.excluded_payments)
        return max_(remuneration - excluded, 0)
