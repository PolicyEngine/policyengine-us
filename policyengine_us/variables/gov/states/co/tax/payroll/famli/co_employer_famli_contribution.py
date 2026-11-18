from policyengine_us.model_api import *


class co_employer_famli_contribution(Variable):
    value_type = float
    entity = Person
    label = "Colorado employer FAMLI contribution"
    documentation = (
        "Employer-side Colorado FAMLI premium: the employer half for employers "
        "with 10 or more employees, plus the part of the permitted employee "
        "half the employer does not deduct, which it is treated as electing "
        "to pay (7 CCR 1107-1 s. 1.4(6)(A))."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.CO
    reference = (
        "https://olls.info/crs/crs2025-title-08.pdf#page=222",
        # PDF pages 7-8
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12341&fileName=7%20CCR%201107-1#page=7",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.co.tax.payroll.famli
        liable = person("employer_headcount", period) >= p.employer_headcount_threshold
        taxable_wages = person("co_famli_taxable_wages", period)
        employer_share = where(liable, p.employer_rate * taxable_wages, 0)
        undeducted = 1 - person("state_payroll_premium_deduction_share", period)
        return employer_share + undeducted * p.employee_rate * taxable_wages
