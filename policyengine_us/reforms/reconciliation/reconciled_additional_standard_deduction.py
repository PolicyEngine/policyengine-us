from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant
import numpy as np


def create_reconciled_additional_standard_deduction() -> Reform:
    class additional_standard_deduction(Variable):
        value_type = float
        entity = TaxUnit
        label = "Additional standard deduction"
        unit = USD
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/63#f"

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.irs.deductions.standard
            filing_status = tax_unit("filing_status", period)
            amount_per = p.aged_or_blind.amount[filing_status]
            base_deduction = amount_per * tax_unit("aged_blind_count", period)
            agi = tax_unit("adjusted_gross_income", period)
            p_ref = parameters(period).gov.contrib.reconciliation.additional_sd_reduction
            joint = filing_status == filing_status.possible_values.JOINT
            phase_out_amount = where(joint, p_ref.rate.joint.calc(agi), p_ref.rate.other.calc(agi))
            return max_(base_deduction - phase_out_amount, 0)

    class tax_unit_itemizes(Variable):
        value_type = bool
        entity = TaxUnit
        label = "Itemizes tax deductions"
        unit = USD
        documentation = "Whether tax unit elects to itemize deductions rather than claim the standard deduction."
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            if parameters(period).gov.simulation.branch_to_determine_itemization:
                # determine federal itemization behavior by comparing tax liability
                tax_liability_if_itemizing = tax_unit(
                    "tax_liability_if_itemizing", period
                )
                tax_liability_if_not_itemizing = tax_unit(
                    "tax_liability_if_not_itemizing", period
                )
                return tax_liability_if_itemizing < tax_liability_if_not_itemizing
            else:
                # determine federal itemization behavior by comparing deductions
                standard_deduction = tax_unit("standard_deduction", period)
                p = parameters(period).gov.irs.deductions
                itemized_deductions = tax_unit(
                    "itemized_taxable_income_deductions", period
                )
                additional_sd = tax_unit("additional_standard_deduction", period)
                total_itm_deduction = itemized_deductions + additional_sd
                return total_itm_deduction > standard_deduction



    def modify_parameters(parameters):
        parameters.gov.irs.deductions.deductions_if_itemizing.update(
            start=instant("2026-01-01"),
            stop=instant("2035-12-31"),
            value=[
                "charitable_deduction",
                "interest_deduction",
                "salt_deduction",
                "medical_expense_deduction",
                "casualty_loss_deduction",
                "qualified_business_income_deduction",
                "wagering_losses_deduction",
                "tuition_and_fees_deduction",
                "misc_deduction",
            ],
        )
        return parameters

    class reform(Reform):
        def apply(self):
            self.update_variable(additional_standard_deduction)
            self.update_variable(tax_unit_itemizes)
            self.modify_parameters(modify_parameters)

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
