from policyengine_us.model_api import *


class id_grocery_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho grocery credit"
    unit = USD
    definition_period = YEAR
    defined_for = "StateCode.ID"

    def formula(tax_unit, period, parameters):
        #### Defining paths to gc and income_threshold directories to access params ####
        path_gc = parameters(period).gov.states.id.tax.income.credits.gc
        path_inc_thre = parameters(
            period
        ).gov.states.id.tax.income.credits.income_threshold

        #### Get ages for both the head and spouse ####
        age_head = tax_unit("age_head", period)
        age_spouse = tax_unit("age_spouse ", period)
        filing_status = tax_unit("filing_status", period)
        income = tax_unit("id_agi", period)
        total_dependents = tax_unit.sum(dependent)  # need to check!

        #### Define constants ####
        all_credits = 0

        age_threshold = path_gc.age_older_eligibility  # 65
        age_amount = path_gc.aged_amount  # 20
        base_credit = path_gc.amount  # 100

        joint_income_bar = path_inc_thre.two_aged  # 27_800, 28_700
        one_joint_income_bar = path_inc_thre.one_aged.JOINT  # 26_450, 27_300
        one_single_and_others_income_bar = (
            path_inc_thre.one_aged.SINGLE
        )  # 14_250, 14_700

        #### Logic for calcualting grocery credit ####
        # Create boolean variables head_aged and spouse_aged to identify if they're over 65
        head_aged = age_head >= age_threshold  # 65
        spouse_aged = age_spouse >= age_threshold  # 65

        joint = filing_status == filing_status.possible_values.JOINT
        if joint:  # filling jointly
            if (head_aged == True) & (spouse_aged == True):
                if income < joint_income_bar:
                    all_credits = (age_amount + base_credit) * 2
                else:
                    all_credits = (
                        age_amount + base_credit
                    ) * 2 + base_credit * (total_dependents + 2)

            elif (head_aged == True) | (spouse_aged == True):
                if income < one_joint_income_bar:
                    all_credits = age_amount + base_credit * 2
                else:
                    all_credits = age_amount + base_credit * (
                        total_dependents + 2
                    )

            elif (head_aged == False) & (spouse_aged == False):
                all_credits = base_credit * (total_dependents + 2)

        else:  # filling single, means here's only the head
            if head_aged == True:
                if income < one_single_and_others_income_bar:
                    all_credits = base_credit + age_amount
                else:
                    all_credits = age_amount + base_credit * (
                        total_dependents + 1
                    )
            else:
                all_credits = base_credit * (total_dependents + 1)

        return all_credits
