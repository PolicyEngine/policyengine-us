from policyengine_us.model_api import *


class ny_mctmt_employer_quarterly_payroll_expense(Variable):
    value_type = float
    entity = Person
    label = "New York MCTMT employer quarterly payroll expense"
    documentation = (
        "Employer quarterly payroll expense proxy for the MCTMT. If no override "
        "is provided, this assumes the employer's payroll expense in the "
        "worker's MCTMT zone is proportional to the worker's annual wages and "
        "employer headcount, evenly distributed across quarters."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.NY

    def formula(person, period, parameters):
        override = person("employer_quarterly_payroll_expense_override", period)
        proxy = (
            person("payroll_tax_gross_wages", period)
            * person("employer_headcount", period)
            / 4
        )
        return where(override >= 0, override, proxy)
