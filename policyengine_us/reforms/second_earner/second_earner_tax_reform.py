from policyengine_us.model_api import *


def create_second_earner_tax() -> Reform:
    class taxable_income_person(Variable):
        value_type = float
        entity = Person
        label = "IRS taxable income for each person"
        unit = USD
        definition_period = YEAR

        def formula(person, period, parameters):
            agi = person("adjusted_gross_income_person", period)
            exemptions = person.tax_unit("exemptions", period) / 2
            deductions = (
                person.tax_unit("taxable_income_deductions", period) / 2
            )
            is_tax_unit_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
            return max_(0, agi - exemptions - deductions) * is_tax_unit_head_or_spouse


#TODO: Attribute dependent income to the head




    class income_tax_main_rates(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "Income tax main rates"
        reference = "https://www.law.cornell.edu/uscode/text/26/1"
        unit = USD

        def formula(tax_unit, period, parameters):
            person = tax_unit.members
            full_taxable_income = person("taxable_income_person", period)
            cg_exclusion = tax_unit("capital_gains_excluded_from_taxable_income", period) / 2
            taxinc = max_(0, full_taxable_income - cg_exclusion)
            p = parameters(period).gov.irs.income
            bracket_tops = p.bracket.thresholds
            bracket_rates = p.bracket.rates
            filing_status = tax_unit("filing_status", period)
            
            # Determine primary and secondary earner incomes based on income size
            is_tax_unit_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
            earner_taxinc = taxinc * is_tax_unit_head_or_spouse
            max_income = max_(earner_taxinc)
            is_primary_earner = (earner_taxinc == max_income) & (earner_taxinc > 0)
            is_secondary_earner = is_tax_unit_head_or_spouse & ~is_primary_earner
            
            taxable_income_primary_earner = where(is_primary_earner, taxinc, 0).sum()
            taxable_income_secondary_earner = where(is_secondary_earner, taxinc, 0).sum()

            # Calculate primary earner tax using actual filing status
            primary_earner_tax = 0
            bracket_bottom = 0
            for i in range(1, len(list(bracket_rates.__iter__())) + 1):
                b = str(i)
                bracket_top = bracket_tops[b][filing_status]
                primary_earner_tax += bracket_rates[b] * amount_between(
                    taxable_income_primary_earner, bracket_bottom, bracket_top
                )
                bracket_bottom = bracket_top

            # Calculate secondary earner tax using single filing status
            secondary_earner_tax = 0
            bracket_bottom = 0
            filing_statuses = filing_status.possible_values
            single_status = filing_statuses.SINGLE
            for i in range(1, len(list(bracket_rates.__iter__())) + 1):
                b = str(i)
                bracket_top = bracket_tops[b][single_status]
                secondary_earner_tax += bracket_rates[b] * amount_between(
                    taxable_income_secondary_earner, bracket_bottom, bracket_top
                )
                bracket_bottom = bracket_top

            return primary_earner_tax + secondary_earner_tax





    class reform(Reform):
        def apply(self):
            self.update_variable(taxable_income_person)

    return reform


def create_second_earner_tax_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_second_earner_tax()

    p = parameters(period).gov.contrib.second_earner_reform

    if p.in_effect:
        return create_second_earner_tax()
    else:
        return None


second_earner_tax_reform = create_second_earner_tax_reform(
    None, None, bypass=True
)
