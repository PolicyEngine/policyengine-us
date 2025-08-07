from policyengine_us.model_api import *


class me_property_tax_fairness_credit_benefit_base(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = "Maine property tax fairness credit benefit base"
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
        # legal code does not mention surviving spouse, but it does appear in the tax form
        surviving_spouse = filing_status == filing_statuses.SURVIVING_SPOUSE
        # Separate filers are ineligible so not included in this select statement.
        # This benefit base does not include the senior amount that takes effect in 2024.
        return select(
            [
                single,
                joint_no_child | head_of_household_one_child,
                joint_with_child
                | head_of_household_multiple_child
                | surviving_spouse,
            ],
            [
                p.benefit_base.single,
                p.benefit_base.head_of_household_one_child,
                p.benefit_base.joint_or_head_of_household_multiple_children,
            ],
            default=0,
        )
