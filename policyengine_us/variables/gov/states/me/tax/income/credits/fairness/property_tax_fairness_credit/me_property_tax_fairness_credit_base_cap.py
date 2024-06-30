from policyengine_us.model_api import *


class me_property_tax_fairness_credit_base_cap(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = "Maine property tax fairness credit base cap"
    definition_period = YEAR
    defined_for = StateCode.ME

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.me.tax.income.credits.fairness.property_tax
        dependents = tax_unit("ctc_qualifying_children", period)
        filing_status = tax_unit("filing_status", period)
        filing_statuses = filing_status.possible_values
        single = filing_status == filing_statuses.SINGLE
        joint = filing_status == filing_statuses.JOINT
        joint_no_child = joint & (dependents == 0)
        head_of_household = filing_status == filing_statuses.HEAD_OF_HOUSEHOLD
        head_of_household_one_child = head_of_household & (
            dependents <= p.dependent_count_threshold
        )
        joint_with_child = joint & (dependents >= p.dependent_count_threshold)
        head_of_household_multiple_child = head_of_household & (
            dependents > p.dependent_count_threshold
        )
        # legal code does not mention widow, but it does appear in the tax form
        widow = filing_status == filing_statuses.SURVIVING_SPOUSE
        # Separate filers are ineligible so not included in this select statement.
        benefit_base = select(
            [
                single,
                joint_no_child | head_of_household_one_child,
                joint_with_child | head_of_household_multiple_child | widow,
            ],
            [
                p.benefit_base.single,
                p.benefit_base.head_of_household_one_child,
                p.benefit_base.joint_or_head_of_household_multiple_children,
            ],
        )

        greater_age_head_spouse = tax_unit("greater_age_head_spouse", period)
        senior_benefit_base = p.benefit_base.senior.calc(
            greater_age_head_spouse
        )
        consider_senior = max_(senior_benefit_base, benefit_base)
        senior_benefit_apply = senior_benefit_base != 0
        adjusted_benefit_base = where(
            senior_benefit_apply, consider_senior, benefit_base
        )

        countable_rent_property_tax = tax_unit(
            "me_property_tax_fairness_credit_countable_rent_property_tax",
            period,
        )
        capped_benefit_base = min_(
            adjusted_benefit_base, countable_rent_property_tax
        )
        income = tax_unit(
            "me_sales_and_property_tax_fairness_credit_income", period
        )
        income_rate = income * p.rate.income
        uncapped_credit = max_(capped_benefit_base - income_rate, 0)
        cap = p.cap.calc(greater_age_head_spouse)

        return min_(uncapped_credit, cap)
