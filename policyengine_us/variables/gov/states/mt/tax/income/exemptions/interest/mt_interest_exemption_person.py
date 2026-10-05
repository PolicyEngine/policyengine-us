from policyengine_us.model_api import *


class mt_interest_exemption_person(Variable):
    value_type = float
    entity = Person
    label = "Montana interest exemption for each person"
    unit = USD
    definition_period = YEAR
    reference = "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2022_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=25"
    defined_for = "mt_interest_exemption_eligible_person"

    def formula(person, period, parameters):
        # Allocate the interest exemption to head/spouse based on share of interest income.
        interest_income = person("taxable_interest_income", period)
        total_interest_income = person.tax_unit.sum(interest_income)
        total_deduction = person.tax_unit("mt_interest_exemption", period)
        deduction_rate = np.zeros_like(total_interest_income)
        mask = total_interest_income != 0
        deduction_rate[mask] = interest_income[mask] / total_interest_income[mask]
        return total_deduction * deduction_rate
