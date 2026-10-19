from policyengine_us.model_api import *


class co_employee_famli_contribution(Variable):
    value_type = float
    entity = Person
    label = "Colorado employee FAMLI contribution"
    documentation = (
        "Employee-side Colorado FAMLI premium. The employer remits the premium "
        "and may deduct up to half of it from wages (C.R.S. 8-13.3-507(5)); "
        "this is that permitted share times state_payroll_premium_deduction_share."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.CO
    reference = (
        "https://olls.info/crs/crs2025-title-08.pdf",
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12341&fileName=7%20CCR%201107-1",
    )

    def formula(person, period, parameters):
        rate = parameters(period).gov.states.co.tax.payroll.famli.employee_rate
        permitted = rate * person("co_famli_taxable_wages", period)
        return permitted * person("state_payroll_premium_deduction_share", period)
