from policyengine_us.model_api import *


class nj_employee_unemployment_insurance_contribution(Variable):
    value_type = float
    entity = Person
    label = "New Jersey employee unemployment insurance contribution"
    documentation = (
        "Total mandatory worker unemployment contribution. For governmental "
        "reimbursable employers, this includes both the 0.0825 percent remittance "
        "and the 0.30 percent withheld in the employer's benefit trust fund."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.NJ
    reference = (
        # PDF pages 60-61, 81
        "https://www.nj.gov/labor/myunemployment/assets/pdfs/UI_statute.pdf#page=60",
        "https://www.nj.gov/labor/ea/assets/PDFs/EmployerAcctsGuide.pdf#page=22",
    )

    def formula_2015_01_01(person, period, parameters):
        p = parameters(period).gov.states.nj.tax.payroll.unemployment
        taxable_wages = person("nj_employee_unemployment_taxable_wages", period)
        return p.employee_rate * taxable_wages
