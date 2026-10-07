from policyengine_us.model_api import *


class ar_agi_indiv(Variable):
    value_type = float
    entity = Person
    label = "Arkansas adjusted gross income for each individual"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dfa.arkansas.gov/wp-content/uploads/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=14",
        # Filing Status 4: the primary's income in column A, the spouse's in B
        "https://www.dfa.arkansas.gov/wp-content/uploads/2025_AR1000F_and_AR1000NR_Instructions.pdf#page=12",
        # Parents filing separately: the parent with the greater taxable income
        "https://www.law.cornell.edu/uscode/text/26/1#g_5_B",
        "https://www.irs.gov/instructions/i8814",
    )
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        gross_income = person("ar_gross_income_indiv", period)
        income_exemptions = person("ar_exemptions", period)
        net_income = max_(gross_income - income_exemptions, 0)
        # Each spouse's column holds their own income. Dependents' income goes
        # on the column of the spouse with the greater income.
        return move_dependent_amounts_to_filer(person, period, net_income)
