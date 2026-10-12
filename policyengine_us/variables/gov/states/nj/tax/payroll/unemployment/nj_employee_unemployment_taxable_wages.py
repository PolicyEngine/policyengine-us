from policyengine_us.model_api import *


class nj_employee_unemployment_taxable_wages(Variable):
    value_type = float
    entity = Person
    label = "New Jersey employee unemployment and workforce taxable wages"
    documentation = (
        "Covered wages subject to New Jersey employee UI and WF/SWF contributions, "
        "including federal pre-tax payroll deductions. The employee wage base is "
        "separate from the larger TDI and FLI employee wage base."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.NJ
    reference = (
        "https://www.nj.gov/labor/myunemployment/assets/pdfs/UI_statute.pdf#page=47",
        "https://www.nj.gov/labor/ea/assets/PDFs/EmployerAcctsGuide.pdf#page=20",
    )

    def formula_2015_01_01(person, period, parameters):
        p = parameters(period).gov.states.nj.tax.payroll.unemployment
        return min_(
            max_(0, person("employment_income", period)),
            p.employee_taxable_wage_base,
        )
