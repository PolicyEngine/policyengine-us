from policyengine_us.model_api import *


class va_spouse_tax_adjustment(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia Spouse Tax Adjustment"
    defined_for = "va_spouse_tax_adjustment_eligible"
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=19"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        # Line 4, enter the taxable income
        taxable_income = tax_unit("va_taxable_income", period)
        # Line 5, enter the AGI less exemptions:
        agi_less_exemptions = person("va_agi_less_exemptions_person", period)
        capped_agi_less_exemptions = max_(agi_less_exemptions, 0)
        # If the tax filer is the head or the spouse of the tax unit, take his/hers corresponding value
        # Set the value for dependent amount to infinity as we will need the smaller amount for
        # further calculations
        smaller_agi_less_exemptions = tax_unit.min(
            where(head_or_spouse, capped_agi_less_exemptions, np.inf)
        )
        # Line 6, subtract
        reduced_taxable_income = max_(
            taxable_income - smaller_agi_less_exemptions, 0
        )
        # Line 7, divide taxable income in half
        p = parameters(
            period
        ).gov.states.va.tax.income.exemptions.spouse_tax_adjustment
        half_of_taxable_income = taxable_income / p.divisor
        # Line 8, take the smaller of the tax calculated on line 5 or line 7
        p1 = parameters(period).gov.states.va.tax.income
        smaller_agi_or_taxable_income = min_(
            p1.rates.calc(smaller_agi_less_exemptions),
            p1.rates.calc(half_of_taxable_income),
        )
        # Line 9, enter the larger of the tax calculated on line 6 or line 7
        larger_reduced_taxable_income_or_halved_taxable_income = max_(
            p1.rates.calc(reduced_taxable_income),
            p1.rates.calc(half_of_taxable_income),
        )
        # Line 10, add line 8 and line 9
        addition_of_tax = (
            smaller_agi_or_taxable_income
            + larger_reduced_taxable_income_or_halved_taxable_income
        )
        # Line 11, enter income tax before credits
        income_tax_before_credits = tax_unit(
            "va_income_tax_before_non_refundable_credits", period
        )
        # Line 12, subtract line 10 from line 11
        reduced_tax = max_(income_tax_before_credits - addition_of_tax, 0)
        # The value cannot exceed a certain threshold
        return min_(reduced_tax, p.cap)
