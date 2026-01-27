from policyengine_us.model_api import *


def create_ma_h3262_income_tax_reform() -> Reform:
    """
    Massachusetts House Bill H.3262 - Income Tax Reform

    This bill makes two key changes to Massachusetts income tax:
    1. Increases the Part B tax rate from 5.0% to 6.0%
    2. Increases personal exemptions:
       - Single/MFS (Bracket 1): $4,400 -> $6,600
       - Head of Household (Bracket 1A): $6,800 -> $10,200
       - Married Filing Jointly (Bracket 2): $8,800 -> $13,200

    Reference: https://malegislature.gov/Bills/194/H3262
    """

    class ma_h3262_part_b_taxable_income_exemption(Variable):
        value_type = float
        entity = TaxUnit
        label = "MA H3262 Part B taxable income exemption"
        unit = USD
        definition_period = YEAR
        reference = "https://malegislature.gov/Bills/194/H3262"
        defined_for = StateCode.MA

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.ma.h3262
            in_effect = p.in_effect

            if not in_effect:
                # Use standard calculation when reform not in effect
                tax = parameters(period).gov.states.ma.tax.income
                filing_status = tax_unit("filing_status", period)
                return tax.exemptions.personal[filing_status]

            # H3262 exemptions
            filing_status = tax_unit("filing_status", period)
            personal_exemption = p.exemptions.personal[filing_status]

            # Add other exemptions (blind, aged, dependent) from standard law
            tax = parameters(period).gov.states.ma.tax.income
            person = tax_unit.members
            dependent = person("is_tax_unit_dependent", period)

            # Blind exemptions
            blind = person("is_blind", period)
            count_blind = tax_unit.sum(~dependent & blind)
            blind_exemption = tax.exemptions.blind * count_blind

            # Aged exemptions
            age = person("age", period)
            count_aged = tax_unit.sum(
                ~dependent & (age >= tax.exemptions.aged.age)
            )
            aged_exemption = tax.exemptions.aged.amount * count_aged

            # Dependent exemptions
            count_dependents = tax_unit("tax_unit_dependents", period)
            dependent_exemption = tax.exemptions.dependent * count_dependents

            # Medical expense deduction for itemizers
            itemizes = tax_unit("tax_unit_itemizes", period)
            federal_medical_expense_deduction = tax_unit(
                "medical_expense_deduction", period
            )
            medical_dental_exemption = itemizes * federal_medical_expense_deduction

            return (
                personal_exemption
                + dependent_exemption
                + aged_exemption
                + blind_exemption
                + medical_dental_exemption
            )

    class ma_part_b_taxable_income_exemption(Variable):
        value_type = float
        entity = TaxUnit
        label = "MA Part B taxable income exemption"
        unit = USD
        definition_period = YEAR
        reference = "https://malegislature.gov/Bills/194/H3262"
        defined_for = StateCode.MA

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.ma.h3262
            in_effect = p.in_effect

            tax = parameters(period).gov.states.ma.tax.income
            person = tax_unit.members
            filing_status = tax_unit("filing_status", period)
            dependent = person("is_tax_unit_dependent", period)

            # Personal exemption - use H3262 values if in effect
            if in_effect:
                personal_exemption = p.exemptions.personal[filing_status]
            else:
                personal_exemption = tax.exemptions.personal[filing_status]

            # Blind exemptions
            blind = person("is_blind", period)
            count_blind = tax_unit.sum(~dependent & blind)
            blind_exemption = tax.exemptions.blind * count_blind

            # Aged exemptions
            age = person("age", period)
            count_aged = tax_unit.sum(
                ~dependent & (age >= tax.exemptions.aged.age)
            )
            aged_exemption = tax.exemptions.aged.amount * count_aged

            # Dependent exemptions
            count_dependents = tax_unit("tax_unit_dependents", period)
            dependent_exemption = tax.exemptions.dependent * count_dependents

            # Medical expense deduction for itemizers
            itemizes = tax_unit("tax_unit_itemizes", period)
            federal_medical_expense_deduction = tax_unit(
                "medical_expense_deduction", period
            )
            medical_dental_exemption = itemizes * federal_medical_expense_deduction

            return (
                personal_exemption
                + dependent_exemption
                + aged_exemption
                + blind_exemption
                + medical_dental_exemption
            )

    class ma_income_tax_before_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "MA income tax before credits"
        unit = USD
        definition_period = YEAR
        reference = "https://malegislature.gov/Bills/194/H3262"
        defined_for = StateCode.MA

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.ma.h3262
            in_effect = p.in_effect

            part_a_dividends = tax_unit(
                "ma_part_a_taxable_dividend_income", period
            )
            part_a_capital_gains = tax_unit(
                "ma_part_a_taxable_capital_gains_income", period
            )
            part_b = tax_unit("ma_part_b_taxable_income", period)
            part_c = tax_unit("ma_part_c_taxable_income", period)
            rates = parameters(period).gov.states.ma.tax.income.rates
            exempt = tax_unit("is_ma_income_tax_exempt", period)

            # Use H3262 rate if in effect, otherwise standard rate
            part_b_rate = where(in_effect, p.part_b_rate, rates.part_b)

            tax_on_income = (
                rates.part_a.dividends * part_a_dividends
                + rates.part_a.capital_gains * part_a_capital_gains
                + part_b_rate * part_b
                + rates.part_c * part_c
            )
            total_taxable_income = (
                part_a_dividends + part_a_capital_gains + part_b + part_c
            )
            additional_tax = rates.additional.calc(total_taxable_income)
            return where(exempt, 0, tax_on_income + additional_tax)

    class reform(Reform):
        def apply(self):
            self.update_variable(ma_part_b_taxable_income_exemption)
            self.update_variable(ma_income_tax_before_credits)

    return reform


def create_ma_h3262_income_tax_reform_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_ma_h3262_income_tax_reform()

    p = parameters(period).gov.contrib.states.ma.h3262

    if p.in_effect:
        return create_ma_h3262_income_tax_reform()
    else:
        return None


ma_h3262_income_tax_reform = create_ma_h3262_income_tax_reform_reform(
    None, None, bypass=True
)
