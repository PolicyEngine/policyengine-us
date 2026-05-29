from policyengine_us.model_api import *


class ca_payroll_tax_gross_wages(Variable):
    value_type = float
    entity = Person
    label = "California payroll tax gross wages"
    documentation = (
        "Wages subject to California payroll taxes, including HSA payroll "
        "contributions that are excluded from the federal FICA wage base."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.CA
    reference = "https://edd.ca.gov/siteassets/files/pdf_pub_ctr/de231tp.pdf#page=7"

    def formula(person, period, parameters):
        return max_(
            0,
            min_(
                person("employment_income", period),
                person("payroll_tax_gross_wages", period)
                + person("health_savings_account_payroll_contributions", period),
            ),
        )
