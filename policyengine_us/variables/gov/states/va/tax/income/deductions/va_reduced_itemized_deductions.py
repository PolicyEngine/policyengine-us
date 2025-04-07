from policyengine_us.model_api import *


class va_reduced_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia reduced itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/sites/default/files/taxforms/individual-income-tax/2021/schedule-2021.pdf"
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        p_va = parameters(period).gov.states.va.tax.income.deductions.itemized

        # Part A: If AGI from federal return is over a certain amount, then
        # limitations to the itemized deduction are applied
        # Line 1 - sum of medical exepens ded., capped state and local tax,
        # interest ded., charitable ded., and casualty loss ded.
        applicable_ded = add(
            tax_unit,
            period,
            p_va.reduction.applicable,
        )
        # Line 2 medical expense ded., interest ded., casualty loss ded., and gambling losses
        reducible_ded = add(
            tax_unit,
            period,
            p_va.reduction.reducible,
        )
        # Line 3 - subtract Line 2 from line 1
        excess_ded = max_(applicable_ded - reducible_ded, 0)
        # If 0 - no reduction
        # Line 4 - IRS deduction rate of excess

        # The federal limitation on itemized deductions does not apply during the TCJA period
        # Virginia still applies the limitation

        # Here, we use a parameter that mostly keeps in line with the IRS's;
        # Virginia follows the IRS, except for TCJA-related policies, hence we
        # remove anything TCJA related, but keep everything else coupled to the IRS

        # Shortcut to the full parameter, not parameter at instant, for IRS itemized limitations
        full_irs_param: Parameter = (
            parameters.gov.irs.deductions.itemized.limitation
        )

        va_itemized_deduction_rate = (
            full_irs_param.itemized_deduction_rate.clone()
        )

        # Eliminate infinite values created by the TCJA's elimination of this param
        va_itemized_deduction_rate.values_list = [
            entry
            for entry in va_itemized_deduction_rate.values_list
            if not (entry.value == np.inf or entry.value == -np.inf)
        ]

        excess_ded_fraction = excess_ded * va_itemized_deduction_rate(period)
        # Line 5 Federal AGI
        federal_agi = tax_unit("adjusted_gross_income", period)
        # Line 6 - applicable amount
        filing_status = tax_unit("filing_status", period)
        applicable_amount = p_va.applicable_amount[filing_status]
        # Line 7 - excess
        excess = max_(federal_agi - applicable_amount, 0)
        # Line 8 - excess times federal item. ded. AGI rate

        # Here again, Virginia follows the IRS, except for TCJA-related policies,
        # and we'll need to eliminate infinite values created by TCJA abolishing param
        va_agi_rate = full_irs_param.agi_rate.clone()
        va_agi_rate.values_list = [
            entry
            for entry in va_agi_rate.values_list
            if not (entry.value == np.inf or entry.value == -np.inf)
        ]

        agi_adjustment = va_agi_rate(period) * excess
        # Line 9 - min of line 4 and line 8
        va_itm_deds_adjustment = min_(agi_adjustment, excess_ded_fraction)
        # Output from Part A (Line 1 - Line 9)
        # Line 17 of the VA Schedule A
        reduced_selected_ded = max_(applicable_ded - va_itm_deds_adjustment, 0)

        # Part B: state and local income tax modification
        # Form Part A - line 11 - Line 9 divided by line 3
        adjustment_fraction = np.zeros_like(excess_ded)
        mask = excess_ded != 0
        adjustment_fraction[mask] = (
            va_itm_deds_adjustment[mask] / excess_ded[mask]
        )
        # Part B Line 13 - capped state and local income tax

        # Line 14 - Multiply line 11 by line 13
        capped_state_and_local_tax = tax_unit(
            "va_capped_state_and_local_sales_or_income_tax", period
        )

        state_and_local_tax_adj = (
            capped_state_and_local_tax * adjustment_fraction
        )
        # Line 15 - Subtract Line 14 from Line 13
        reduced_state_and_local_tax = max_(
            capped_state_and_local_tax - state_and_local_tax_adj, 0
        )
        return max_(reduced_selected_ded - reduced_state_and_local_tax, 0)
