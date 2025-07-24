from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant
import numpy as np


def create_reconciled_auto_loan_interest_ald() -> Reform:
    class auto_loan_interest_ald(Variable):
        value_type = float
        entity = TaxUnit
        label = "Auto loan interest ALD"
        unit = USD
        definition_period = YEAR
        reference = "https://budget.house.gov/imo/media/doc/one_big_beautiful_bill_act_-_full_bill_text.pdf#page=765"

        def formula(tax_unit, period, parameters):
            auto_loan_interest = add(tax_unit, period, ["auto_loan_interest"])
            p = parameters(
                period
            ).gov.contrib.reconciliation.auto_loan_interest_ald
            capped_interest = min_(auto_loan_interest, p.cap)
            # Get filing status.
            filing_status = tax_unit("filing_status", period)

            # Get the phaseout start amount based on filing status (line 4).
            phaseout_start = p.phase_out.start[filing_status]
            agi_pre_ald = tax_unit(
                "adjusted_gross_income_pre_auto_loan_interest_ald", period
            )
            # Get the excess amount, if any, in thousands of dollars (rounded up) [lines 5 and 6].
            excess = max_(agi_pre_ald - phaseout_start, 0)
            increments = np.ceil(excess / p.phase_out.increment)

            # Calculate the excess part phase out amount (line 7).
            phase_out_amount = increments * p.phase_out.step
            return max_(capped_interest - phase_out_amount, 0)

    class adjusted_gross_income_pre_auto_loan_interest_ald(Variable):
        value_type = float
        entity = TaxUnit
        label = "Adjusted gross income before the Auto Loan Interest ALD"
        unit = USD
        definition_period = YEAR
        reference = "https://budget.house.gov/imo/media/doc/one_big_beautiful_bill_act_-_full_bill_text.pdf#page=765"

        # OBBBA phases out the auto loan interest ALD with respect to AGI.
        # This creates a circular reference, since it also reduces AGI.
        # To get around this drafting error, we phase out the auto loan interest ALD
        # with respect to a version of AGI that excludes the auto loan interest ALD.
        def formula(tax_unit, period, parameters):
            gross_income = add(tax_unit, period, ["irs_gross_income"])
            above_the_line_deductions = tax_unit(
                "above_the_line_deductions", period
            )
            agi = gross_income - above_the_line_deductions
            if parameters(period).gov.contrib.ubi_center.basic_income.taxable:
                agi += add(tax_unit, period, ["basic_income"])
            return agi

    class adjusted_gross_income(Variable):
        value_type = float
        entity = TaxUnit
        label = "Adjusted gross income"
        unit = USD
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/62"

        def formula(tax_unit, period, parameters):
            gross_income = add(tax_unit, period, ["irs_gross_income"])
            above_the_line_deductions = tax_unit(
                "above_the_line_deductions", period
            )
            auto_loan_interest_ald = tax_unit("auto_loan_interest_ald", period)
            agi = gross_income - (
                above_the_line_deductions + auto_loan_interest_ald
            )
            p = parameters(
                period
            ).gov.contrib.reconciliation.auto_loan_interest_ald
            if p.senate_version.applies:
                agi = gross_income - above_the_line_deductions
            if parameters(period).gov.contrib.ubi_center.basic_income.taxable:
                agi += add(tax_unit, period, ["basic_income"])
            return agi

    class taxable_income_deductions(Variable):
        value_type = float
        entity = TaxUnit
        label = "Taxable income deductions"
        unit = USD
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            itemizes = tax_unit("tax_unit_itemizes", period)
            deductions_if_itemizing = tax_unit(
                "taxable_income_deductions_if_itemizing", period
            )
            deductions_if_not_itemizing = tax_unit(
                "taxable_income_deductions_if_not_itemizing", period
            )
            auto_loan_interest_ald = tax_unit("auto_loan_interest_ald", period)
            p = parameters(
                period
            ).gov.contrib.reconciliation.auto_loan_interest_ald
            if p.senate_version.applies:
                deductions_if_itemizing = (
                    deductions_if_itemizing + auto_loan_interest_ald
                )
                deductions_if_not_itemizing = (
                    deductions_if_not_itemizing + auto_loan_interest_ald
                )
            return where(
                itemizes, deductions_if_itemizing, deductions_if_not_itemizing
            )

    class reform(Reform):
        def apply(self):
            self.update_variable(auto_loan_interest_ald)
            self.update_variable(adjusted_gross_income)
            self.update_variable(
                adjusted_gross_income_pre_auto_loan_interest_ald
            )
            self.update_variable(taxable_income_deductions)

    return reform


def create_reconciled_auto_loan_interest_ald_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_reconciled_auto_loan_interest_ald()

    p = parameters.gov.contrib.reconciliation.auto_loan_interest_ald

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_reconciled_auto_loan_interest_ald()
    else:
        return None


reconciled_auto_loan_interest_ald = (
    create_reconciled_auto_loan_interest_ald_reform(None, None, bypass=True)
)
