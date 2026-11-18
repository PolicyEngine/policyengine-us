from policyengine_us.model_api import *


class medicaid_ltss_gross_unearned_income(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS gross monthly unearned income"
    unit = USD
    definition_period = MONTH
    documentation = (
        "Each person's own monthly unearned income before Medicaid LTSS "
        "income exclusions or qualified income trust deposits. Defaults "
        "to one twelfth of the existing gross SSI unearned-income sources, "
        "including pensions and Social Security, without SSI exclusions "
        "or spousal deeming. A nonnegative "
        "medicaid_ltss_reported_gross_unearned_income supplies the actual "
        "month's amount for that person. Unspecified people retain the "
        "annual-source default independently of other people's monthly "
        "reports. Each spouse reports their own income; the model "
        "combines it when couple budgeting applies."
    )
    reference = "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=6"

    def formula(person, period, parameters):
        reported = person("medicaid_ltss_reported_gross_unearned_income", period)
        use_annual = reported == -1
        if not use_annual.any():
            return max_(reported, 0)
        annual_default = max_(
            person("ssi_unearned_income", period.this_year) / MONTHS_IN_YEAR, 0
        )
        return where(use_annual, annual_default, max_(reported, 0))
