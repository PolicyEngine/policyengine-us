from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class ga_low_income_credit_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia low income credit"
    unit = USD
    definition_period = YEAR
    reference = "https://dor.georgia.gov/document/document/2022-it-511-individual-income-tax-booklet/download"
    defined_for = StateCode.GA

    def formula(tax_unit, period, parameters):
        # We follow the legal code, which says (in addition to head and spouse):
        # "multiplied by the number of dependents which the taxpayer is entitled to claim."
        # The tax form excludes adult dependents:
        # "Exemptions are self, spouse and natural or legally adopted children"
        exemptions = tax_unit("exemptions_count", period)
        p = parameters(period).gov.states.ga.tax.income.credits.low_income
        # age threshold
        age_threshold = p.supplement_age_eligibility
        aged_head = (tax_unit("age_head", period) >= age_threshold).astype(
            int
        )  # if so, return 1, otherwise return 0
        aged_spouse = (tax_unit("age_spouse", period) >= age_threshold).astype(
            int
        )  # if so, return 1, otherwise return 0
        aged_count = aged_head + aged_spouse
        total_exemptions = aged_count + exemptions
        federal_agi = tax_unit("adjusted_gross_income", period)
        amount_per_exemption = p.amount.calc(federal_agi)
        return total_exemptions * amount_per_exemption


class ga_low_income_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia low income credit"
    unit = USD
    definition_period = YEAR
    reference = "https://dor.georgia.gov/document/document/2022-it-511-individual-income-tax-booklet/download"
    defined_for = StateCode.GA

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.ga.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "ga_income_tax_before_non_refundable_credits",
            "ga_low_income_credit",
            "ga_low_income_credit_potential",
        )
