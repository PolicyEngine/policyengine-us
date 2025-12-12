from policyengine_us.model_api import *
import numpy as np


class ms_total_exemptions_indiv(Variable):
    value_type = float
    entity = Person
    label = "Mississippi total exemptions when married couples file separately"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MS
    reference = "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=6"

    def formula(person, period, parameters):
        # Get tax unit level data
        total_exemptions = person.tax_unit("ms_total_exemptions", period)
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)

        # Get AGI and deductions for each person
        agi = person("ms_agi", period)
        deductions = person("ms_deductions_indiv", period)

        # Get tax rate schedule
        rate = parameters(period).gov.states.ms.tax.income.rate

        # For heads and spouses in tax units with both, optimize exemption allocation
        tax_unit = person.tax_unit
        heads_agi = tax_unit.sum(agi * is_head)
        spouses_agi = tax_unit.sum(agi * is_spouse)
        heads_deductions = tax_unit.sum(deductions * is_head)
        spouses_deductions = tax_unit.sum(deductions * is_spouse)

        # Check if this is a married couple (has both head and spouse)
        has_spouse = tax_unit.any(is_spouse)

        # For single filers, give all exemptions to the head
        single_allocation = is_head * total_exemptions

        # For married couples filing separately, optimize the allocation
        # We'll try different splits to minimize total tax
        # Strategy: allocate exemptions to equalize taxable incomes where possible

        # Calculate the difference in pre-exemption income
        income_diff = (
            heads_agi - heads_deductions - (spouses_agi - spouses_deductions)
        )

        # Optimal allocation: try to equalize taxable incomes
        # If head has higher income, give more exemptions to head
        head_optimal_exemptions = where(
            income_diff > 0,
            min_(total_exemptions, (income_diff + total_exemptions) / 2),
            max_(0, (income_diff + total_exemptions) / 2),
        )
        spouse_optimal_exemptions = total_exemptions - head_optimal_exemptions

        # Ensure allocations are non-negative and sum to total
        head_optimal_exemptions = max_(
            0, min_(head_optimal_exemptions, total_exemptions)
        )
        spouse_optimal_exemptions = max_(
            0, min_(spouse_optimal_exemptions, total_exemptions)
        )

        # Return the optimal allocation for each person
        married_allocation = (
            is_head * head_optimal_exemptions
            + is_spouse * spouse_optimal_exemptions
        )

        return where(has_spouse, married_allocation, single_allocation)
