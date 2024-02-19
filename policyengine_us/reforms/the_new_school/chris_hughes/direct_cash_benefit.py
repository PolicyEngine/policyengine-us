from policyengine_us.model_api import *


def create_direct_cash_benefit() -> Reform:
    class direct_cash_benefit(Variable):
        value_type = float
        entity = Household
        label = "Direct Cash Benefit"
        unit = USD
        documentation = (
            "Direct cash benefit provided to households based on their income."
        )
        definition_period = YEAR
        reference = "https://racepowerpolicy.org/wp-content/uploads/2023/12/Direct-Cash-Payments-in-the-Next-Recession_FINAL.pdf"

        def formula(household, period, parameters):
            household_income = household("household_net_income", period)
            count_people = household("household_count_people", period)
            p_chris_hughes = parameters(
                period
            ).gov.contrib.the_new_school.chris_hughes.direct_cash_benefit

            income_threshold = p_chris_hughes.household_income_limit
            phase_out_threshold = p_chris_hughes.phase_out.phase_out_threshold
            if household_income >= phase_out_threshold:
                # Calculate phase-out amount linearly decreasing from 6480 to 0
                phase_out_cash_amount = (
                    p_chris_hughes.phase_out.phase_out_cash_amount
                )
                phase_out_rate = phase_out_cash_amount / (
                    income_threshold - phase_out_threshold
                )
                phase_out_amount = (
                    income_threshold - household_income
                ) * phase_out_rate
                return count_people * max(0, phase_out_amount)
            else:
                return count_people * p_chris_hughes.amount.cal(
                    household_income
                )

    class reform(Reform):
        def apply(self):
            self.update_variable(direct_cash_benefit)

    return reform


# whether need this reform class? function?


def create_cash_benefit_reform(household, period, bypass: bool = False):
    if bypass:
        return create_direct_cash_benefit()

    p_chris_hughes = parameters(
        period
    ).gov.contrib.the_new_school.chris_hughes.direct_cash_benefit
    household_income = household("household_net_income", period)

    if household_income <= p_chris_hughes.household_income_limit:
        return create_direct_cash_benefit()
    else:
        return None


direct_cash_benefit = create_cash_benefit_reform(None, None, bypass=True)
# why need this?
