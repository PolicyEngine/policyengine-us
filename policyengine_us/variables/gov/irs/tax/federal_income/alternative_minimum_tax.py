from policyengine_us.model_api import *


class amt_income(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "AMT taxable income"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/55#b_2"

    def formula(tax_unit, period, parameters):
        taxable_income = tax_unit("taxable_income", period)
        # Add back excluded deductions
        itemizing = tax_unit("tax_unit_itemizes", period)
        standard_deduction = tax_unit("standard_deduction", period)
        salt_deduction = tax_unit("salt_deduction", period)
        excluded_deductions = where(
            itemizing,
            salt_deduction,
            standard_deduction,
        )
        amt_inc = taxable_income + excluded_deductions
        amt = parameters(period).gov.irs.income.amt
        filing_status = tax_unit("filing_status", period)
        separate_addition = max_(
            0,
            min_(
                amt.exemption.amount[filing_status],
                amt.exemption.phase_out.rate
                * max_(0, amt_inc - amt.exemption.separate_limit),
            ),
        ) * (filing_status == filing_status.possible_values.SEPARATE)
        return amt_inc + separate_addition


class regular_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Regular tax before credits"
    documentation = "Regular tax on regular taxable income before credits"
    unit = USD

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        dwks1 = tax_unit("taxable_income", period)

        capital_gains = parameters(period).gov.irs.capital_gains.brackets

        dwks16 = min_(capital_gains.thresholds["1"][filing_status], dwks1)
        dwks17 = min_(tax_unit("dwks14", period), dwks16)
        dwks20 = dwks16 - dwks17
        lowest_rate_tax = capital_gains.rates["1"] * dwks20
        # Break in worksheet lines
        dwks13 = tax_unit("dwks13", period)
        dwks21 = min_(dwks1, dwks13)
        dwks22 = dwks20
        dwks23 = max_(0, dwks21 - dwks22)
        dwks25 = min_(capital_gains.thresholds["2"][filing_status], dwks1)
        dwks19 = tax_unit("dwks19", period)
        dwks26 = min_(dwks19, dwks20)
        dwks27 = max_(0, dwks25 - dwks26)
        dwks28 = min_(dwks23, dwks27)
        dwks29 = capital_gains.rates["2"] * dwks28
        dwks30 = dwks22 + dwks28
        dwks31 = dwks21 - dwks30
        dwks32 = capital_gains.rates["3"] * dwks31
        # Break in worksheet lines
        dwks33 = min_(
            tax_unit("dwks09", period),
            add(tax_unit, period, ["unrecaptured_section_1250_gain"]),
        )
        dwks10 = tax_unit("dwks10", period)
        dwks34 = dwks10 + dwks19
        dwks36 = max_(0, dwks34 - dwks1)
        dwks37 = max_(0, dwks33 - dwks36)

        p = parameters(period).gov.irs.income

        dwks38 = p.amt.capital_gains.capital_gain_excess_tax_rate * dwks37
        # Break in worksheet lines
        dwks39 = dwks19 + dwks20 + dwks28 + dwks31 + dwks37
        dwks40 = dwks1 - dwks39
        dwks41 = 0.28 * dwks40

        # Compute regular tax using bracket rates and thresholds
        reg_taxinc = max_(0, dwks19)
        bracket_tops = p.bracket.thresholds
        bracket_rates = p.bracket.rates
        reg_tax = 0
        bracket_bottom = 0
        for i in range(1, len(list(bracket_rates.__iter__())) + 1):
            b = str(i)
            bracket_top = bracket_tops[b][filing_status]
            reg_tax += bracket_rates[b] * amount_between(
                reg_taxinc, bracket_bottom, bracket_top
            )
            bracket_bottom = bracket_top

        # Return to worksheet lines
        dwks42 = reg_tax
        dwks43 = sum(
            [
                dwks29,
                dwks32,
                dwks38,
                dwks41,
                dwks42,
                lowest_rate_tax,
            ]
        )
        dwks44 = tax_unit("income_tax_main_rates", period)
        dwks45 = min_(dwks43, dwks44)
        return where(tax_unit("has_qdiv_or_ltcg", period), dwks45, dwks44)


class alternative_minimum_tax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Alternative Minimum Tax"
    unit = USD
    documentation = "Alternative Minimum Tax (AMT) liability"

    def formula(tax_unit, period, parameters):
        amt_income = tax_unit("amt_income", period)
        # Form 6251, Part II top
        amt = parameters(period).gov.irs.income.amt
        phase_out = amt.exemption.phase_out
        filing_status = tax_unit("filing_status", period)
        line29 = max_(
            0,
            (
                amt.exemption.amount[filing_status]
                - phase_out.rate
                * max_(0, amt_income - phase_out.start[filing_status])
            ),
        )
        age_head = tax_unit("age_head", period)
        child = parameters(period).gov.irs.dependent.ineligible_age
        young_head = (age_head != 0) & (age_head < child.non_student)
        no_or_young_spouse = tax_unit("age_spouse", period) < child.non_student
        adj_earnings = tax_unit("filer_adjusted_earnings", period)
        if period.start.year >= 2019:
            child_amount = 0
        else:
            child_amount = amt.exemption.child.amount

        line29_cap_applies = young_head & no_or_young_spouse
        line29_cap = where(
            line29_cap_applies, adj_earnings + child_amount, np.inf
        )
        line29_capped = min_(line29, line29_cap)
        line30 = max_(0, amt_income - line29_capped)
        brackets = amt.brackets
        bracket_fraction = where(
            filing_status == filing_status.possible_values.SEPARATE,
            0.5,
            1.0,
        )
        amount_over_threshold = (
            line30 - brackets.thresholds["1"] * bracket_fraction
        )
        line3163 = brackets.rates["1"] * line30 + brackets.rates["2"] * max_(
            0, amount_over_threshold
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
        line40 = min_(line30, line39)
        line41 = max_(0, line30 - line40)
        amount_over_threshold = max_(
            0, line41 - amt.brackets.thresholds["1"] * bracket_fraction
        )
        line42 = (
            amt.brackets.rates["1"] * line41
            + amt.brackets.rates["2"] * amount_over_threshold
        )
        line44 = dwks14
        cg = amt.capital_gains.brackets
        line45 = max_(0, cg.thresholds["1"][filing_status] - line44)
        line46 = min_(line30, line37)
        line47 = min_(line45, line46)
        cgtax1 = line47 * cg.rates["1"]
        line48 = line46 - line47
        line51 = dwks19
        line52 = line45 + line51
        line53 = max_(0, cg.thresholds["2"][filing_status] - line52)
        line54 = min_(line48, line53)
        cgtax2 = line54 * cg.rates["2"]
        line56 = line47 + line54
        line57 = where(line41 == line56, 0, line46 - line56)
        linex2 = where(line41 == line56, 0, max_(0, line54 - line48))
        cgtax3 = line57 * cg.rates["3"]
        line61 = where(
            line38 == 0,
            0,
            0.25 * max_(0, (line30 - line41 - line56 - line57 - linex2)),
        )
        line62 = line42 + cgtax1 + cgtax2 + cgtax3 + line61
        line64 = min_(line3163, line62)
        line31 = where(form_6251_part_iii_required, line64, line3163)

        # Form 6251, Part II bottom
        line32 = tax_unit("foreign_tax_credit", period)
        line33 = line31 - line32
        return max_(
            0,
            line33
            - max_(
                0,
                (
                    tax_unit("regular_tax_before_credits", period)
                    - line32
                    - tax_unit("form_4972_lumpsum_distributions", period)
                ),
            ),
        )
