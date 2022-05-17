from openfisca_us.model_api import *


class c62100(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "AMT taxable income"
    unit = USD
    documentation = "Alternative Minimum Tax (AMT) taxable income"

    def formula(tax_unit, period, parameters):
        # Form 6251, Part I
        adjusted_gross_income = tax_unit("adjusted_gross_income", period)
        e00700 = add(tax_unit, period, ["salt_refund_income"])
        c62100_if_no_standard = (
            adjusted_gross_income
            - e00700
            - tax_unit("taxable_income_deductions_if_itemizing", period)
            + max_(
                0,
                min_(
                    tax_unit("medical_expense_deduction", period),
                    0.025 * adjusted_gross_income,
                ),
            )
            + tax_unit("salt_deduction", period)
        )
        c62100 = where(
            tax_unit("standard_deduction", period) == 0,
            c62100_if_no_standard,
            adjusted_gross_income - e00700,
        ) + tax_unit(
            "amt_non_agi_income", period
        )  # add income not in AGI but considered income for AMT
        amt = parameters(period).irs.income.amt
        filing_status = tax_unit("filing_status", period)
        separate_addition = max_(
            0,
            min_(
                amt.exemption.amount[filing_status],
                amt.exemption.phaseout.rate
                * (c62100 - amt.exemption.separate_limit),
            ),
        ) * (filing_status == filing_status.possible_values.SEPARATE)
        return c62100 + separate_addition


amt_income = variable_alias("amt_income", c62100)


class c09600(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Alternative Minimum Tax"
    unit = USD
    documentation = "Alternative Minimum Tax (AMT) liability"

    def formula(tax_unit, period, parameters):
        c62100 = tax_unit("c62100", period)
        # Form 6251, Part II top
        amt = parameters(period).irs.income.amt
        phaseout = amt.exemption.phaseout
        filing_status = tax_unit("filing_status", period)
        line29 = max_(
            0,
            (
                amt.exemption.amount[filing_status]
                - phaseout.rate
                * max_(0, c62100 - phaseout.start[filing_status])
            ),
        )
        age_head = tax_unit("age_head", period)
        child = amt.exemption.child
        young_head = (age_head != 0) & (age_head < child.max_age)
        no_or_young_spouse = tax_unit("age_spouse", period) < child.max_age
        line29 = where(
            young_head & no_or_young_spouse,
            min_(line29, tax_unit("filer_earned", period) + child.amount),
            line29,
        )
        line30 = max_(0, c62100 - line29)
        brackets = amt.brackets
        amount_over_threshold = line30 - brackets.thresholds["1"] / tax_unit(
            "sep", period
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
            0, line41 - amt.brackets.thresholds["1"] / tax_unit("sep", period)
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
        foreign_tax_credit = tax_unit("foreign_tax_credit", period)

        # Form 6251, Part II bottom
        line32 = where(
            tax_unit("amt_form_completed", period),
            tax_unit("foreign_tax_credit", period),
            foreign_tax_credit,
        )
        line33 = line31 - line32
        return max_(
            0,
            line33
            - max_(
                0,
                (
                    tax_unit("taxbc", period)
                    - foreign_tax_credit
                    - tax_unit("c05700", period)
                ),
            ),
        )


alternative_minimum_tax = variable_alias("alternative_minimum_tax", c09600)
