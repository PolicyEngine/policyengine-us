from policyengine_us.model_api import *


class medicaid_ltss_gross_earned_income(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS gross monthly earned income"
    unit = USD
    definition_period = MONTH
    documentation = (
        "Each person's own monthly work income before Medicaid LTSS income "
        "exclusions or qualified income trust deposits. Defaults to one "
        "twelfth of the existing gross SSI earned-income sources, which "
        "include wages and self-employment income without SSI exclusions "
        "or spousal deeming. A nonnegative "
        "medicaid_ltss_reported_gross_earned_income supplies the actual "
        "month's amount for that person, including work income outside "
        "those sources. Unspecified people retain the annual-source "
        "default independently of other people's monthly reports. Each "
        "spouse reports their own income; the model combines it when "
        "couple budgeting applies."
    )
    reference = "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=5"

    def formula(person, period, parameters):
        reported = person("medicaid_ltss_reported_gross_earned_income", period)
        annual_default = max_(person("ssi_earned_income", period.this_year) / 12, 0)
        return where(reported == -1, annual_default, max_(reported, 0))
