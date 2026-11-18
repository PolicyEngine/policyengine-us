from policyengine_us.model_api import *


class ia_net_income(Variable):
    value_type = float
    entity = Person
    label = "Iowa net income"
    documentation = (
        "Iowa net income in the head's and spouse's columns of the return. A "
        "tax unit dependent's income belongs on the dependent's own Iowa "
        "return, so a dependent's amount is zero."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdf",
        # PDF page 7: Status 3, married filing separately on a combined return
        "https://revenue.iowa.gov/media/2650/download?inline#page=7",
        "https://revenue.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdf",
        # PDF pages 4, 8: who must file (c), and the note to dependents
        # filing their own returns
        "https://revenue.iowa.gov/media/2721/download?inline#page=4",
        # Iowa Code 422.7: net income starts from federal adjusted gross
        # income, which leaves out a dependent's income.
        "https://www.legis.iowa.gov/docs/code/2022/422.7.pdf",
        # Iowa Code 422.13(1)(a): a person claimed as a dependent on another
        # person's return files their own return with net income of $5,000
        # or more.
        "https://www.legis.iowa.gov/docs/code/2022/422.13.pdf",
    )
    defined_for = StateCode.IA

    def formula(person, period, parameters):
        gross_income = person("ia_gross_income", period)
        income_adjustments = person("ia_income_adjustments", period)
        net_income = gross_income - income_adjustments
        # Each spouse's column holds their own income. A dependent's income
        # goes on the dependent's own return, not on the filer's.
        is_dependent = person("is_tax_unit_dependent", period)
        return where(is_dependent, 0, net_income)
