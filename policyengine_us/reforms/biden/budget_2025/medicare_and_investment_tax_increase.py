from policyengine_us.model_api import *


def create_medicare_and_investment_tax_increase() -> Reform:
    class additional_medicare_tax(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "Additional Medicare Tax"
        unit = USD
        documentation = (
            "Additional Medicare Tax from Form 8959 (included in payrolltax)"
        )

        def formula(tax_unit, period, parameters):
            amc = parameters(period).gov.irs.payroll.medicare.additional
            # Wage and self-employment income are taxed the same.
            ELEMENTS = [
                "irs_employment_income",
                "taxable_self_employment_income",
            ]
            wages_plus_se = add(tax_unit, period, ELEMENTS)
            exclusion = amc.exclusion[tax_unit("filing_status", period)]
            base = max_(0, wages_plus_se - exclusion)
            base_tax = amc.rate * base
            p_reform = parameters(
                period
            ).gov.contrib.biden.budget_2025.medicare
            add_excess = max_(wages_plus_se - p_reform.threshold, 0)
            add_tax = p_reform.rate * add_excess
            return base_tax + add_tax

    class net_investment_income_tax(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "Net Investment Income Tax"
        reference = "https://www.law.cornell.edu/uscode/text/26/1411"
        unit = USD

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.irs.investment.net_investment_income_tax
            threshold = p.threshold[tax_unit("filing_status", period)]
            agi = tax_unit("adjusted_gross_income", period)
            excess_agi = max_(0, agi - threshold)
            investment_income = tax_unit("net_investment_income", period)
            capped_investment_income = max_(0, investment_income)
            base = min_(
                capped_investment_income,
                excess_agi,
            )
            base_tax = p.rate * base
            p_reform = parameters(
                period
            ).gov.contrib.biden.budget_2025.net_investment_income
            add_excess_agi = max_(agi - p_reform.threshold, 0)
            lesser_of_excess_and_inv_income = min_(
                add_excess_agi, capped_investment_income
            )
            add_tax = p_reform.rate * lesser_of_excess_and_inv_income
            return base_tax + add_tax

    class reform(Reform):
        def apply(self):
            self.update_variable(additional_medicare_tax)
            self.update_variable(net_investment_income_tax)

    return reform


def create_medicare_and_investment_tax_increase_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_medicare_and_investment_tax_increase()

    p = parameters(period).gov.contrib.biden.budget_2025

    if (p.medicare.rate > 0) | (p.net_investment_income.rate > 0):
        return create_medicare_and_investment_tax_increase()
    else:
        return None


medicare_and_investment_tax_increase = (
    create_medicare_and_investment_tax_increase_reform(None, None, bypass=True)
)
