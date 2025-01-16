from policyengine_us.model_api import *

class pr_low_income_credit(Variable):
    value_type = float
    entity = Person
    label = "Puerto Rico earned income credit"
    unit = USD
    definition_period = YEAR
    reference = ""
    defined_for = "pr_earned_income_credit_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.territories.pr.tax.income.credits.earned_income

        # workflow:
        # Calculate credit amount pre phase out
        # Income * phase_in_rate capped at max_credit
        # Calculate the phase_out
        # p.phase_out_rate.calc(income)
        # Calculate final value
        # credit - phase_out
        earned_gross_income = 10_000 # PLACEHOLDER for earned gross income, person level

        # calculate phase in 
        # what does p.phase_out_amount.threshold return? which threshold? 
        upper_threshold = p.phase_out_amount.threshold[] 
        # if gross income > upper threshold, calculate [bottom threshold * phase_in] - [(upper - bottom threshold) * phase_out]
        # if gross income > lower threshold, calculate [bottom threshold (i.e. 10k) * phase_in] - [(income - bottom threshold) * phase_out]
        # ELSE, calculate income * phase_in_rate

        
        return False