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
            deductions = person("taxable_income_deductions_person", period)
            return max_(0, agi - exemptions - deductions)

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
            is_tax_unit_head_or_spouse = person(
                "is_tax_unit_head_or_spouse", period
            )
            cg_exclusion = (
                tax_unit("capital_gains_excluded_from_taxable_income", period)
                / 2
            ) * is_tax_unit_head_or_spouse
            taxinc = max_(0, full_taxable_income - cg_exclusion)
            p = parameters(period).gov.irs.income
            bracket_tops = p.bracket.thresholds
            bracket_rates = p.bracket.rates
            filing_status = tax_unit("filing_status", period)

            # Determine primary and secondary earner incomes based on income size
            is_tax_unit_head = person("is_tax_unit_head", period)
            is_tax_unit_dependent = person("is_tax_unit_dependent", period)

            # Add dependent income to head's income
            dependent_income = (taxinc * is_tax_unit_dependent).sum()
            earner_taxinc = taxinc * is_tax_unit_head_or_spouse
            earner_taxinc = where(
                is_tax_unit_head,
                earner_taxinc + dependent_income,
                earner_taxinc,
            )

            max_income = tax_unit.max(earner_taxinc)
            is_primary_earner = earner_taxinc == max_income
            is_secondary_earner = (
                is_tax_unit_head_or_spouse & ~is_primary_earner
            )

            taxable_income_primary_earner = where(
                is_primary_earner, earner_taxinc, 0
            ).sum()
            taxable_income_secondary_earner = where(
                is_secondary_earner, earner_taxinc, 0
            ).sum()

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
            single_status = "SINGLE"
            for i in range(1, len(list(bracket_rates.__iter__())) + 1):
                b = str(i)
                bracket_top = bracket_tops[b][single_status]
                secondary_earner_tax += bracket_rates[b] * amount_between(
                    taxable_income_secondary_earner,
                    bracket_bottom,
                    bracket_top,
                )
                bracket_bottom = bracket_top

            return primary_earner_tax + secondary_earner_tax

    class basic_standard_deduction_person(Variable):
        value_type = float
        entity = Person
        label = "Basic standard deduction"
        definition_period = YEAR
        unit = USD
        reference = "https://www.law.cornell.edu/uscode/text/26/63#c_2"

        def formula(person, period, parameters):
            std = parameters(period).gov.irs.deductions.standard
            filing_status = person.tax_unit("filing_status", period)
            separate_filer_itemizes = person.tax_unit(
                "separate_filer_itemizes", period
            )
            dependent_elsewhere = person.tax_unit(
                "head_is_dependent_elsewhere", period
            )

            # Determine primary and secondary earners
            earned_income = person("earned_income", period)
            is_tax_unit_head_or_spouse = person(
                "is_tax_unit_head_or_spouse", period
            )
            is_tax_unit_head = person("is_tax_unit_head", period)
            is_tax_unit_dependent = person("is_tax_unit_dependent", period)

            # Add dependent income to head's income
            dependent_income = (earned_income * is_tax_unit_dependent).sum()
            earner_taxinc = earned_income * is_tax_unit_head_or_spouse
            earner_taxinc = where(
                is_tax_unit_head,
                earner_taxinc + dependent_income,
                earner_taxinc,
            )

            max_income = person.tax_unit.max(earner_taxinc)
            is_primary_earner = (earner_taxinc == max_income) & (
                (
                    earner_taxinc
                    > person.tax_unit.max(
                        where(~is_tax_unit_head, earner_taxinc, 0)
                    )
                )
                | is_tax_unit_head
            )
            is_secondary_earner = (
                is_tax_unit_head_or_spouse & ~is_primary_earner
            )

            # Calculate primary earner deduction using actual filing status
            primary_deduction = std.amount[filing_status]

            # Calculate secondary earner deduction using single filing status
            secondary_deduction = std.amount["SINGLE"]
            # Combine deductions based on earner status
            standard_deduction = where(
                is_primary_earner,
                primary_deduction,
                where(is_secondary_earner, secondary_deduction, 0),
            )

            standard_deduction_if_dependent = min_(
                standard_deduction,
                max_(
                    std.dependent.additional_earned_income
                    + person.tax_unit("tax_unit_earned_income", period),
                    std.dependent.amount,
                ),
            )

            return select(
                [
                    separate_filer_itemizes,
                    dependent_elsewhere,
                    True,
                ],
                [
                    0,
                    standard_deduction_if_dependent,
                    standard_deduction,
                ],
            )

    class standard_deduction_person(Variable):
        value_type = float
        entity = Person
        label = "Standard deduction for each person"
        unit = USD
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/63#c"

        def formula(person, period, parameters):
            basic_deduction = person("basic_standard_deduction_person", period)
            additional_deduction = (
                person.tax_unit("additional_standard_deduction", period) / 2
            )
            bonus_deduction = (
                person.tax_unit("bonus_guaranteed_deduction", period) / 2
            )
            return basic_deduction + additional_deduction + bonus_deduction

    class taxable_income_deductions_person(Variable):
        value_type = float
        entity = Person
        label = "Taxable income deductions for each person"
        unit = USD
        definition_period = YEAR

        def formula(person, period, parameters):
            itemizes = person.tax_unit("tax_unit_itemizes", period)
            deductions_if_itemizing = (
                person.tax_unit(
                    "taxable_income_deductions_if_itemizing", period
                )
                / 2
            )
            standard_deduction = person("standard_deduction_person", period)
            qbid = person("qualified_business_income_deduction_person", period)
            return where(
                itemizes, deductions_if_itemizing, standard_deduction + qbid
            )

    class reform(Reform):
        def apply(self):
            self.update_variable(taxable_income_person)
            self.update_variable(income_tax_main_rates)
            self.update_variable(basic_standard_deduction_person)
            self.update_variable(standard_deduction_person)
            self.update_variable(taxable_income_deductions_person)

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
