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
            exemption_amount = person.tax_unit("exemptions", period)
            is_joint = person.tax_unit("tax_unit_is_joint", period)
            exemptions = where(
                is_joint, exemption_amount / 2, exemption_amount
            )
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

    class additional_standard_deduction_person(Variable):
        value_type = float
        entity = Person
        label = "Additional standard deduction for each person"
        unit = USD
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/63#f"

        def formula(person, period, parameters):
            std = parameters(period).gov.irs.deductions.standard
            filing_status = person.tax_unit("filing_status", period)
            is_blind = person("is_blind", period).astype(int)
            age_threshold = parameters(
                period
            ).gov.irs.deductions.standard.aged_or_blind.age_threshold
            is_aged = (person("age", period) >= age_threshold).astype(int)
            aged_blind = is_blind + is_aged
            primary_earner = person("is_primary_earner", period)
            amount = where(
                primary_earner,
                std.aged_or_blind.amount[filing_status],
                std.aged_or_blind.amount["SINGLE"],
            )
            return aged_blind * amount

    class bonus_guaranteed_deduction_person(Variable):
        value_type = float
        entity = Person
        label = "Bonus guaranteed deduction"
        unit = USD
        definition_period = YEAR
        reference = "https://waysandmeans.house.gov/malliotakis-steel-lead-legislation-to-provide-tax-relief-to-working-families/"

        def formula(person, period, parameters):
            filing_status = person.tax_unit("filing_status", period)
            wftca = parameters(
                period
            ).gov.contrib.congress.wftca.bonus_guaranteed_deduction
            primary_earner = person("is_primary_earner", period)
            amount = where(
                primary_earner,
                wftca.amount[filing_status],
                wftca.amount["SINGLE"],
            )
            agi = person("adjusted_gross_income_person", period)
            threshold = where(
                primary_earner,
                wftca.phase_out.threshold[filing_status],
                wftca.phase_out.threshold["SINGLE"],
            )
            income_in_phase_out_region = max_(agi - threshold, 0)
            reduction = wftca.phase_out.rate * income_in_phase_out_region
            return max_(amount - reduction, 0)

    class standard_deduction_person(Variable):
        value_type = float
        entity = Person
        label = "Standard deduction for each person"
        unit = USD
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/63#c"

        def formula(person, period, parameters):
            basic_deduction = person("basic_standard_deduction_person", period)
            additional_deduction = person(
                "additional_standard_deduction_person", period
            )
            bonus_deduction = person(
                "bonus_guaranteed_deduction_person", period
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
            is_joint = person.tax_unit("tax_unit_is_joint", period)
            deductions_if_itemizing_amount = person.tax_unit(
                "taxable_income_deductions_if_itemizing", period
            )
            deductions_if_itemizing = where(
                is_joint,
                deductions_if_itemizing_amount / 2,
                deductions_if_itemizing_amount,
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
            is_joint = person.tax_unit("tax_unit_is_joint", period)
            divisor = where(is_joint, 2, 1)
            unrecaptured_s_1250_gain = (
                person.tax_unit("unrecaptured_section_1250_gain", period)
                / divisor
            )
            cg_28_pct_rate_gain = (
                person.tax_unit("capital_gains_28_percent_rate_gain", period)
                / divisor
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
            is_joint = tax_unit("tax_unit_is_joint", period)
            divisor = where(is_joint, 2, 1)
            unrecaptured_s_1250_gain = (
                tax_unit("unrecaptured_section_1250_gain", period) / divisor
            )
            qualified_dividends = (
                add(tax_unit, period, ["qualified_dividend_income"]) / divisor
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
            ) / divisor
            return tax_unit.sum(
                main_cg_tax + unrecaptured_gain_tax + remaining_cg_tax
            )

    class amt_excluded_deductions_person(Variable):
        value_type = float
        entity = Person
        definition_period = YEAR
        label = "AMT taxable income excluded deductions"
        unit = USD
        reference = "https://www.law.cornell.edu/uscode/text/26/55#b_2"

        def formula(person, period, parameters):
            itemizing = person.tax_unit("tax_unit_itemizes", period)
            standard_deduction = person("standard_deduction_person", period)
            is_joint = person.tax_unit("tax_unit_is_joint", period)
            divisor = where(is_joint, 2, 1)
            salt_deduction = (
                person.tax_unit("salt_deduction", period) / divisor
            )
            return where(itemizing, salt_deduction, standard_deduction)

    class amt_income_person(Variable):
        value_type = float
        entity = Person
        definition_period = YEAR
        label = "AMT taxable income"
        unit = USD
        reference = "https://www.law.cornell.edu/uscode/text/26/55#b_2"
        defined_for = "is_tax_unit_head_or_spouse"

        def formula(person, period, parameters):
            taxable_income = person("taxable_income_person", period)
            deductions = person("amt_excluded_deductions_person", period)
            is_joint = person.tax_unit("tax_unit_is_joint", period)
            divisor = where(is_joint, 2, 1)
            separate_addition = (
                person.tax_unit("amt_separate_addition", period) / divisor
            )
            return taxable_income + deductions + separate_addition

    class alternative_minimum_tax(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "Alternative Minimum Tax"
        unit = USD
        documentation = "Alternative Minimum Tax (AMT) liability"

        def formula(tax_unit, period, parameters):
            person = tax_unit.members
            amt_income = person("amt_income_person", period)
            # Form 6251, Part II top
            p = parameters(period).gov.irs.income.amt
            phase_out = p.exemption.phase_out
            filing_status = tax_unit("filing_status", period)

            # Split calculations for primary and secondary earners
            is_primary_earner = person("is_primary_earner", period)
            is_secondary_earner = (
                person("is_tax_unit_head_or_spouse", period)
                & ~is_primary_earner
            )
            is_tax_unit_dependent = person("is_tax_unit_dependent", period)

            # Primary earner uses filing status thresholds
            primary_base_exemption = p.exemption.amount[filing_status]
            primary_phase_out_start = phase_out.start[filing_status]

            # Secondary earner uses single thresholds
            secondary_base_exemption = p.exemption.amount["SINGLE"]
            secondary_phase_out_start = phase_out.start["SINGLE"]

            # Calculate income for each earner
            primary_income = where(is_primary_earner, amt_income, 0)
            secondary_income = where(is_secondary_earner, amt_income, 0)
            dependent_income = where(
                is_tax_unit_dependent, amt_income, 0
            ).sum()
            primary_income += (
                dependent_income  # Add dependent income to primary
            )

            # Calculate exemption amounts
            primary_excess = max_(0, primary_income - primary_phase_out_start)
            secondary_excess = max_(
                0, secondary_income - secondary_phase_out_start
            )

            primary_exemption = max_(
                0, primary_base_exemption - phase_out.rate * primary_excess
            )
            secondary_exemption = max_(
                0, secondary_base_exemption - phase_out.rate * secondary_excess
            )

            age_head = tax_unit("age_head", period)
            child = parameters(period).gov.irs.dependent.ineligible_age
            young_head = (age_head != 0) & (age_head < child.non_student)
            no_or_young_spouse = (
                tax_unit("age_spouse", period) < child.non_student
            )
            adj_earnings = person("adjusted_earnings", period)
            child_amount = p.exemption.child.amount

            kiddie_tax_exemption_cap_applies = young_head & no_or_young_spouse
            exemption_cap = where(
                kiddie_tax_exemption_cap_applies,
                adj_earnings + child_amount,
                np.inf,
            )
            primary_exemption = min_(primary_exemption, exemption_cap)
            secondary_exemption = min_(secondary_exemption, exemption_cap)

            # Calculate taxable income
            taxable_income = person("taxable_income_person", period)
            # Do not add back deduction for filers subject to the kiddie tax
            primary_applied_income = where(
                kiddie_tax_exemption_cap_applies,
                where(is_primary_earner, taxable_income, 0),
                primary_income,
            )
            secondary_applied_income = where(
                kiddie_tax_exemption_cap_applies,
                where(is_secondary_earner, taxable_income, 0),
                secondary_income,
            )

            primary_reduced_income = max_(
                0, primary_applied_income - primary_exemption
            )
            secondary_reduced_income = max_(
                0, secondary_applied_income - secondary_exemption
            )

            # Calculate bracket fractions
            primary_bracket_fraction = where(
                filing_status == filing_status.possible_values.SEPARATE,
                0.5,
                1.0,
            )
            secondary_bracket_fraction = (
                1.0  # Single always uses full brackets
            )

            # Calculate tax thresholds
            primary_tax_threshold = (
                p.brackets.thresholds[-1] * primary_bracket_fraction
            )
            secondary_tax_threshold = (
                p.brackets.thresholds[-1] * secondary_bracket_fraction
            )

            lower_rate = p.brackets.rates[0]
            higher_rate = p.brackets.rates[1]

            # Calculate tax for primary earner
            primary_lower_tax = (
                min_(primary_reduced_income, primary_tax_threshold)
                * lower_rate
            )
            primary_higher_tax = (
                max_(0, primary_reduced_income - primary_tax_threshold)
                * higher_rate
            )

            # Calculate tax for secondary earner
            secondary_lower_tax = (
                min_(secondary_reduced_income, secondary_tax_threshold)
                * lower_rate
            )
            secondary_higher_tax = (
                max_(0, secondary_reduced_income - secondary_tax_threshold)
                * higher_rate
            )

            # Combine taxes
            reduced_income_tax = (
                primary_lower_tax
                + primary_higher_tax
                + secondary_lower_tax
                + secondary_higher_tax
            )

            dwks10, dwks13, dwks14, dwks19, e24515 = [
                add(tax_unit, period, [variable])
                for variable in [
                    "dwks10",
                    "dwks13",
                    "dwks14",
                    "dwks19",
                    "unrecaptured_section_1250_gain",
                ]
            ]
            form_6251_part_iii_required = np.any(
                [
                    variable > 0
                    for variable in [
                        dwks10,
                        dwks13,
                        dwks14,
                        dwks19,
                        e24515,
                    ]
                ]
            )

            # Complete Form 6251, Part III
            line37 = dwks13
            line38 = e24515
            line39 = min_(line37 + line38, dwks10)
            line40 = min_(
                primary_reduced_income + secondary_reduced_income, line39
            )
            line41 = max_(
                0, primary_reduced_income + secondary_reduced_income - line40
            )
            line42 = p.brackets.calc(line41)
            line44 = dwks14

            # Apply different thresholds for primary/secondary for capital gains
            cg = p.capital_gains.brackets
            primary_line45 = max_(
                0, cg.thresholds["1"][filing_status] - line44
            )
            secondary_line45 = max_(0, cg.thresholds["1"]["SINGLE"] - line44)

            line46 = min_(
                primary_reduced_income + secondary_reduced_income, line37
            )
            primary_line47 = min_(primary_line45, line46)
            secondary_line47 = min_(secondary_line45, line46)

            cgtax1 = (
                primary_line47 * cg.rates["1"]
                + secondary_line47 * cg.rates["1"]
            )

            line48 = line46 - (primary_line47 + secondary_line47)
            line51 = dwks19

            primary_line52 = primary_line45 + line51
            secondary_line52 = secondary_line45 + line51

            primary_line53 = max_(
                0, cg.thresholds["2"][filing_status] - primary_line52
            )
            secondary_line53 = max_(
                0, cg.thresholds["2"]["SINGLE"] - secondary_line52
            )

            primary_line54 = min_(line48, primary_line53)
            secondary_line54 = min_(line48, secondary_line53)

            cgtax2 = (
                primary_line54 * cg.rates["2"]
                + secondary_line54 * cg.rates["2"]
            )

            line56 = (
                primary_line47
                + secondary_line47
                + primary_line54
                + secondary_line54
            )
            line57 = where(line41 == line56, 0, line46 - line56)
            linex2 = where(
                line41 == line56,
                0,
                max_(0, primary_line54 + secondary_line54 - line48),
            )
            cgtax3 = line57 * cg.rates["3"]

            line61 = where(
                line38 == 0,
                0,
                p.capital_gains.capital_gain_excess_tax_rate
                * max_(
                    0,
                    (
                        primary_reduced_income
                        + secondary_reduced_income
                        - line41
                        - line56
                        - line57
                        - linex2
                    ),
                ),
            )
            line62 = line42 + cgtax1 + cgtax2 + cgtax3 + line61
            line64 = min_(reduced_income_tax, line62)
            line31 = where(
                form_6251_part_iii_required, line64, reduced_income_tax
            )

            # Form 6251, Part II bottom
            is_joint = tax_unit("tax_unit_is_joint", period)
            divisor = where(is_joint, 2, 1)
            line32 = tax_unit("foreign_tax_credit", period) / divisor
            line33 = line31 - line32
            regular_tax_before_credits = (
                tax_unit("regular_tax_before_credits", period) / divisor
            )
            lump_sum_distributions = (
                tax_unit("form_4972_lumpsum_distributions", period) / divisor
            )
            capital_gains = tax_unit("capital_gains_tax", period)
            tax_before_credits = regular_tax_before_credits + capital_gains

            return tax_unit.sum(
                max_(
                    0,
                    line33
                    - max_(
                        0,
                        (tax_before_credits - line32 - lump_sum_distributions),
                    ),
                )
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
            self.update_variable(alternative_minimum_tax)
            self.update_variable(amt_income_person)
            self.update_variable(amt_excluded_deductions_person)
            self.update_variable(bonus_guaranteed_deduction_person)
            self.update_variable(additional_standard_deduction_person)

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
