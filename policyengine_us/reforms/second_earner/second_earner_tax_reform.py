from policyengine_us.model_api import *


def create_second_earner_tax() -> Reform:

    class is_primary_earner(Variable):
        value_type = bool
        entity = Person
        label = "Whether this person is the primary earner in their tax unit"
        definition_period = YEAR

        def formula(person, period, parameters):
            earned_income = person("earned_income", period)
            is_tax_unit_head_or_spouse = person(
                "is_tax_unit_head_or_spouse", period
            )
            is_tax_unit_head = person("is_tax_unit_head", period)
            is_tax_unit_dependent = person("is_tax_unit_dependent", period)

            # Add dependent income to head's income
            dependent_income = (earned_income * is_tax_unit_dependent).sum()
            earner_income = earned_income * is_tax_unit_head_or_spouse
            earner_income = where(
                is_tax_unit_head,
                earner_income + dependent_income,
                earner_income,
            )

            max_income = person.tax_unit.max(earner_income)
            return (earner_income == max_income) & (
                (
                    earner_income
                    > person.tax_unit.max(
                        where(~is_tax_unit_head, earner_income, 0)
                    )
                )
                | is_tax_unit_head
            )

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
            is_tax_unit_dependent = person("is_tax_unit_dependent", period)

            # Add dependent income to head's income
            dependent_income = (taxinc * is_tax_unit_dependent).sum()
            earner_taxinc = taxinc * is_tax_unit_head_or_spouse

            is_primary_earner = person("is_primary_earner", period)
            is_secondary_earner = (
                is_tax_unit_head_or_spouse & ~is_primary_earner
            )

            taxable_income_primary_earner = where(
                is_primary_earner, earner_taxinc + dependent_income, 0
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
            is_tax_unit_head_or_spouse = person(
                "is_tax_unit_head_or_spouse", period
            )
            is_primary_earner = person("is_primary_earner", period)
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

    class net_capital_gain_person(Variable):
        value_type = float
        entity = Person
        label = "Net capital gain"
        unit = USD
        documentation = (
            "The excess of net long-term capital gain over net short-term capital"
            'loss, plus qualified dividends (the definition of "net capital gain"'
            "which applies to 26 U.S.C. § 1(h) from § 1(h)(11))."
        )
        definition_period = YEAR
        reference = dict(
            title="26 U.S. Code § 1222(11)",
            href="https://www.law.cornell.edu/uscode/text/26/1222#11",
        )

        def formula(person, period, parameters):
            lt_capital_gain = person("long_term_capital_gains", period)
            st_capital_loss = -person("short_term_capital_gains", period)
            net_cap_gain = max_(0, lt_capital_gain - st_capital_loss)
            qual_div_income = person("qualified_dividend_income", period)
            return net_cap_gain + qual_div_income

    class adjusted_net_capital_gain_person(Variable):
        value_type = float
        entity = Person
        label = "Adjusted net capital gain"
        unit = USD
        documentation = "The excess of net long-term capital gain over net short-term capital loss."
        definition_period = YEAR
        reference = dict(
            title="26 U.S. Code § 1(h)(3)",
            href="https://www.law.cornell.edu/uscode/text/26/1#h_3",
        )
        defined_for = "is_tax_unit_head_or_spouse"

        def formula(person, period, parameters):
            net_capital_gain = person("net_capital_gain_person", period)
            # The law actually uses the original definition of 'net capital gain' which does not include
            # qualified dividend income, but separately adds qualified dividends here. The definition of
            # 'net capital gain' in the variable 'net_capital_gain' actually has some very specific exclusion
            # criteria for particular types of dividends and companies, so it's not an *exact* fit to the
            # definition here, but it's a good enough approximation. See 26 U.S. Code § 1(h)(11)(B) for the
            # definition of 'net capital gain' for the above variable, and 26 U.S. Code § 1(h)(3) for the definition
            # of adjusted net capital gain (this variable).
            qualified_dividend_income = person(
                "qualified_dividend_income", period
            )
            unrecaptured_s_1250_gain = (
                person.tax_unit("unrecaptured_section_1250_gain", period) / 2
            )
            cg_28_pct_rate_gain = (
                person.tax_unit("capital_gains_28_percent_rate_gain", period)
                / 2
            )
            net_gains_less_dividends = max_(
                0,
                net_capital_gain - qualified_dividend_income,
            )
            reduced_capital_gains = max_(
                net_gains_less_dividends
                - (unrecaptured_s_1250_gain + cg_28_pct_rate_gain),
                0,
            )
            return reduced_capital_gains + qualified_dividend_income

    class capital_gains_tax(Variable):
        value_type = float
        entity = TaxUnit
        label = "Maximum income tax after capital gains tax"
        unit = USD
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            person = tax_unit.members
            net_cg = person("net_capital_gain_person", period)
            taxable_income = person("taxable_income_person", period)
            adjusted_net_cg = min_(
                person("adjusted_net_capital_gain_person", period),
                taxable_income,
            )  # ANCG is referred to in all cases as ANCG or taxable income if less.

            cg = parameters(period).gov.irs.capital_gains

            excluded_cg = tax_unit(
                "capital_gains_excluded_from_taxable_income", period
            )
            non_cg_taxable_income = max_(0, taxable_income - excluded_cg)

            filing_status = tax_unit("filing_status", period)
            is_tax_unit_head_or_spouse = person(
                "is_tax_unit_head_or_spouse", period
            )
            is_primary_earner = person("is_primary_earner", period)
            is_secondary_earner = (
                is_tax_unit_head_or_spouse & ~is_primary_earner
            )
            is_tax_unit_dependent = person("is_tax_unit_dependent", period)
            # Split capital gains between primary and secondary earners
            primary_cg = where(is_primary_earner, adjusted_net_cg, 0)
            secondary_cg = where(is_secondary_earner, adjusted_net_cg, 0)
            dependent_cg = where(
                is_tax_unit_dependent, adjusted_net_cg, 0
            ).sum()
            primary_cg += dependent_cg  # Add dependent gains to primary earner

            # Calculate primary earner capital gains tax (using filing status thresholds)
            first_threshold_primary = cg.brackets.thresholds["1"][
                filing_status
            ]
            second_threshold_primary = cg.brackets.thresholds["2"][
                filing_status
            ]

            # Calculate secondary earner capital gains tax (using single thresholds)
            first_threshold_secondary = cg.brackets.thresholds["1"]["SINGLE"]
            second_threshold_secondary = cg.brackets.thresholds["2"]["SINGLE"]

            # Calculate brackets for primary earner
            primary_cg_in_first = clip(primary_cg, 0, first_threshold_primary)
            primary_cg_in_second = clip(
                primary_cg - first_threshold_primary,
                0,
                second_threshold_primary - first_threshold_primary,
            )
            primary_cg_in_third = max_(
                0, primary_cg - second_threshold_primary
            )

            # Calculate brackets for secondary earner
            secondary_cg_in_first = clip(
                secondary_cg, 0, first_threshold_secondary
            )
            secondary_cg_in_second = clip(
                secondary_cg - first_threshold_secondary,
                0,
                second_threshold_secondary - first_threshold_secondary,
            )
            secondary_cg_in_third = max_(
                0, secondary_cg - second_threshold_secondary
            )

            # Calculate total capital gains tax
            main_cg_tax = (
                (primary_cg_in_first + secondary_cg_in_first)
                * cg.brackets.rates["1"]
                + (primary_cg_in_second + secondary_cg_in_second)
                * cg.brackets.rates["2"]
                + (primary_cg_in_third + secondary_cg_in_third)
                * cg.brackets.rates["3"]
            )

            unrecaptured_s_1250_gain = (
                tax_unit("unrecaptured_section_1250_gain", period) / 2
            )
            qualified_dividends = (
                add(tax_unit, period, ["qualified_dividend_income"]) / 2
            )
            max_taxable_unrecaptured_gain = min_(
                unrecaptured_s_1250_gain,
                max_(0, net_cg - qualified_dividends),
            )
            unrecaptured_gain_deduction = max_(
                non_cg_taxable_income + net_cg - taxable_income,
                0,
            )
            taxable_unrecaptured_gain = max_(
                max_taxable_unrecaptured_gain - unrecaptured_gain_deduction,
                0,
            )

            unrecaptured_gain_tax = (
                cg.unrecaptured_s_1250_rate * taxable_unrecaptured_gain
            )

            remaining_cg_tax = (
                tax_unit("capital_gains_28_percent_rate_gain", period)
                * cg.other_cg_rate
            ) / 2
            return tax_unit.sum(
                main_cg_tax + unrecaptured_gain_tax + remaining_cg_tax
            )

    class reform(Reform):
        def apply(self):
            self.update_variable(taxable_income_person)
            self.update_variable(income_tax_main_rates)
            self.update_variable(basic_standard_deduction_person)
            self.update_variable(standard_deduction_person)
            self.update_variable(taxable_income_deductions_person)
            self.update_variable(is_primary_earner)
            self.update_variable(capital_gains_tax)
            self.update_variable(net_capital_gain_person)
            self.update_variable(adjusted_net_capital_gain_person)

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


# TODO: additional SD and bonus guaranteed deduction logic
