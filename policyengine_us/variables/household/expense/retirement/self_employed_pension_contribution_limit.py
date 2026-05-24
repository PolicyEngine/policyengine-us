from policyengine_us.model_api import *


class self_employed_pension_contribution_limit(Variable):
    value_type = float
    entity = Person
    label = "self-employed pension contribution annual additions limit"
    unit = USD
    documentation = (
        "Section 415(c) annual additions limit for modeled self-employed "
        "pension contributions. Regular IRA contributions are subject to "
        "separate IRA limits, and employee 401(k)/403(b) deferrals are "
        "capped separately by the elective deferral limit."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/415#c"

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.gross_income.retirement_contributions
        compensation = max_(0, person("total_self_employment_income", period))
        return min_(p.limit.annual_additions, compensation)
