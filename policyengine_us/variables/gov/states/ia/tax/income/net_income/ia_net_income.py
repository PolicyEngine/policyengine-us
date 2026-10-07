from policyengine_us.model_api import *


class ia_net_income(Variable):
    value_type = float
    entity = Person
    label = "Iowa net income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdf",
        "https://revenue.iowa.gov/media/2650/download?inline",
        "https://revenue.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdf",
        "https://revenue.iowa.gov/media/2721/download?inline",
        # Status 3: married filing separately on a combined return
        "https://revenue.iowa.gov/media/2650/download?inline#page=7",
        # Parents filing separately: the parent with the greater taxable income
        "https://www.law.cornell.edu/uscode/text/26/1#g_5_B",
        "https://www.irs.gov/instructions/i8814",
    )
    defined_for = StateCode.IA

    def formula(person, period, parameters):
        gross_income = person("ia_gross_income", period)
        income_adjustments = person("ia_income_adjustments", period)
        net_income = gross_income - income_adjustments
        # Each spouse's column holds their own income. Dependents' net income
        # goes on the column of the spouse with the greater net income.
        return move_dependent_amounts_to_filer(person, period, net_income)
