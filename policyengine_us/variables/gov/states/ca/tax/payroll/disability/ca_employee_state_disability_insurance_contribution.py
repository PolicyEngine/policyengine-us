from policyengine_us.model_api import *


class ca_employee_state_disability_insurance_contribution(Variable):
    value_type = float
    entity = Person
    label = "California employee state disability insurance contribution"
    documentation = (
        "Employee-side California State Disability Insurance withholding, "
        "which funds SDI and Paid Family Leave."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.CA
    reference = (
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=UIC&sectionNum=984.",
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=UIC&sectionNum=985.",
        "https://edd.ca.gov/siteassets/files/pdf_pub_ctr/de3395.pdf#page=1",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ca.tax.payroll.disability
        wages = person("ca_payroll_tax_gross_wages", period)
        # UIC 985: contributions apply to wages up to the taxable wage limit
        # through 2023; from 2024 there is no limit.
        taxable_wages = min_(wages, p.taxable_wage_base)
        return p.employee_rate * taxable_wages
