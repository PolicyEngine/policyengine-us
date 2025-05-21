from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant
import numpy as np


def create_reconciled_auto_loan_interest_ald() -> Reform:
    class auto_loan_interest_ald(Variable):
        value_type = float
        entity = TaxUnit
        label = "Per‑cap qualified business income deduction amount for each person"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://www.law.cornell.edu/uscode/text/26/199A#b_1"
            "https://www.irs.gov/pub/irs-prior/p535--2018.pdf"
        )

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
            agi = tax_unit("adjusted_gross_income", period)
            # Get the excess amount, if any, in thousands of dollars (rounded up) [lines 5 and 6].
            excess = max_(agi - phaseout_start, 0)
            increments = np.ceil(excess / p.phase_out.increment)

            # Calculate the excess part phase out amount (line 7).
            phase_out_amount = increments * p.phase_out.step
            return max_(capped_interest - phase_out_amount, 0)

    def modify_parameters(parameters):
        parameters.gov.irs.ald.deductions.update(
            start=instant("2026-01-01"),
            stop=instant("2035-12-31"),
            value=[
                "auto_loan_interest_ald",
                "student_loan_interest_ald",
                "loss_ald",
                "early_withdrawal_penalty",
                "alimony_expense",
                "self_employment_tax_ald",
                "educator_expense",
                "health_savings_account_ald",
                "self_employed_health_insurance_ald",
                "self_employed_pension_contribution_ald",
                "traditional_ira_contributions",
                "qualified_adoption_assistance_expense",
                "us_bonds_for_higher_ed",
                "specified_possession_income",
                "puerto_rico_income",
            ],
        )
        return parameters

    class reform(Reform):
        def apply(self):
            self.update_variable(auto_loan_interest_ald)
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
