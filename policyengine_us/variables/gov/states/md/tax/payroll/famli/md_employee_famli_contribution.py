from policyengine_us.model_api import *


class md_employee_famli_contribution(Variable):
    value_type = float
    entity = Person
    label = "Maryland employee FAMLI contribution"
    documentation = (
        "Employee-side Maryland Family and Medical Leave Insurance "
        "contribution. The employer must deduct the employee share unless it "
        "elects to pay some or all of it (Md. Code, Lab. & Empl. s. "
        "8.3-601(e)(2)); this assumes the employer deducts the full share."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.MD
    reference = (
        "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gle&section=8.3-601&enactments=false",
        "https://regs.maryland.gov/us/md/exec/comar/09.42.02.05",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.md.tax.payroll.famli
        taxable_wages = person("md_famli_taxable_wages", period)
        return p.total_rate * p.employee_share * taxable_wages
