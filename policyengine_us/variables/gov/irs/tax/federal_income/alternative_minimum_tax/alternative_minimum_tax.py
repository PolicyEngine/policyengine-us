from policyengine_us.model_api import *


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
        p = parameters(period).gov.irs.income.amt
        phase_out = p.exemption.phase_out
        filing_status = tax_unit("filing_status", period)
        base_exemption_amount = p.exemption.amount[filing_status]
        income_excess = max_(0, amt_income - phase_out.start[filing_status])
        uncapped_exemption_amount = max_(
            0,
            (base_exemption_amount - phase_out.rate * income_excess),
        )
        age_head = tax_unit("age_head", period)
        child = parameters(period).gov.irs.dependent.ineligible_age
        young_head = (age_head != 0) & (age_head < child.non_student)
        no_or_young_spouse = tax_unit("age_spouse", period) < child.non_student
        adj_earnings = tax_unit("filer_adjusted_earnings", period)
        child_amount = p.exemption.child.amount

        kiddie_tax_exemption_cap_applies = young_head & no_or_young_spouse
        exemption_cap = where(
            kiddie_tax_exemption_cap_applies,
            adj_earnings + child_amount,
            np.inf,
        )
        capped_exemption_amount = min_(
            uncapped_exemption_amount, exemption_cap
        )
        # Line 6
        taxable_income = tax_unit("taxable_income", period)
        # Do not add back deduction for filers subject to the kiddie tax
        applied_income = where(
            kiddie_tax_exemption_cap_applies, taxable_income, amt_income
        )
        reduced_income = max_(0, applied_income - capped_exemption_amount)
        bracket_fraction = where(
            filing_status == filing_status.possible_values.SEPARATE,
            0.5,
            1.0,
        )
        tax_rate_threshold = p.brackets.thresholds[-1] * bracket_fraction
        lower_rate = p.brackets.rates[0]
        higher_rate = p.brackets.rates[1]
        lower_tax = min_(reduced_income, tax_rate_threshold) * lower_rate
        higher_tax = max_(0, reduced_income - tax_rate_threshold) * higher_rate

        # Line 7
        reduced_income_tax = lower_tax + higher_tax
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
        line40 = min_(reduced_income, line39)
        line41 = max_(0, reduced_income - line40)
        line42 = p.brackets.calc(line41)
        line44 = dwks14
        cg = p.capital_gains.brackets
        line45 = max_(0, cg.thresholds["1"][filing_status] - line44)
        line46 = min_(reduced_income, line37)
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
            p.capital_gains.capital_gain_excess_tax_rate
            * max_(0, (reduced_income - line41 - line56 - line57 - linex2)),
        )
        line62 = line42 + cgtax1 + cgtax2 + cgtax3 + line61
        line64 = min_(reduced_income_tax, line62)
        line31 = where(form_6251_part_iii_required, line64, reduced_income_tax)

        # Form 6251, Part II bottom
        line32 = tax_unit("foreign_tax_credit", period)
        line33 = line31 - line32
        regular_tax_before_credits = tax_unit(
            "regular_tax_before_credits", period
        )
        lump_sum_distributions = tax_unit(
            "form_4972_lumpsum_distributions", period
        )
        capital_gains = tax_unit("capital_gains_tax", period)
        tax_before_credits = regular_tax_before_credits + capital_gains
        return max_(
            0,
            line33
            - max_(
                0,
                (tax_before_credits - line32 - lump_sum_distributions),
            ),
        )
