from policyengine_us.model_api import *


class de_agi_indiv(Variable):
    value_type = float
    entity = Person
    label = "Delaware adjusted gross income for each individual when married filing separately"
    unit = USD
    definition_period = YEAR
    reference = (
        # Filing Status 3 or 4: each spouse reports their own income
        "https://revenuefiles.delaware.gov/2025/PITForms_Instructions/Instructions/PIT-RES_Instructions_2025-01.pdf#page=5",
        # Borrowed for dependents' income: parents filing separately report a
        # child's income on the return of the parent with the greater
        # taxable income
        "https://www.law.cornell.edu/uscode/text/26/1#g_5_B",
        "https://www.irs.gov/instructions/i8814",
    )
    defined_for = StateCode.DE

    def formula(person, period, parameters):
        pre_exclusions_agi = person("de_pre_exclusions_agi", period)
        indv_exclusions = person(
            "de_elderly_or_disabled_income_exclusion_indiv", period
        )
        net_income = max_(pre_exclusions_agi - indv_exclusions, 0)
        # On a combined separate return each spouse reports their own income.
        # The dependents' income the model counts here goes on the return of
        # the spouse with the greater income (a modelling convention; see the
        # helper).
        return move_dependent_amounts_to_filer(person, period, net_income)
