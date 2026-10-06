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
        # The tax unit exemption counts only the head's and spouse's interest
        # (mt_interest_exemption), so the shares do too: a tax unit dependent's
        # interest is on the dependent's own return.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        interest_income = person("taxable_interest_income", period) * head_or_spouse
        total_interest_income = person.tax_unit.sum(interest_income)
        total_deduction = person.tax_unit("mt_interest_exemption", period)
        deduction_rate = np.zeros_like(total_interest_income)
        mask = total_interest_income != 0
        deduction_rate[mask] = interest_income[mask] / total_interest_income[mask]
        return total_deduction * deduction_rate
