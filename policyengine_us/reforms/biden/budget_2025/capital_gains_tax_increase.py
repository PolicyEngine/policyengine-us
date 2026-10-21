from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.tax.federal_income.foreign_earned_income_exclusion.section_911_net_capital_gain_other_than_dividends import (
    section_911_net_capital_gain_other_than_dividends,
)
from policyengine_us.variables.gov.irs.tax.federal_income.capital_gains.capital_gains_tax import (
    limit_to_tax_at_main_rates,
    rate_gain_taxed_at_28_percent,
)


def create_capital_gains_tax_increase() -> Reform:
    class capital_gains_tax(Variable):
        value_type = float
        entity = TaxUnit
        label = "Maximum income tax after capital gains tax"
        unit = USD
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            # As in the baseline formula, a taxpayer excluding foreign earned
            # income applies the rates to taxable income plus the excluded
            # amount, with gains reduced by any capital gain excess
            # (26 U.S.C. 911(f)).
            net_cg = tax_unit("section_911_net_capital_gain", period)
            taxable_income = tax_unit(
                "taxable_income_plus_section_911_exclusion", period
            )
            adjusted_net_cg = min_(
                tax_unit("section_911_adjusted_net_capital_gain", period),
                taxable_income,
            )  # ANCG is referred to in all cases as ANCG or taxable income if less.

            cg = parameters(period).gov.irs.capital_gains

            excluded_cg = tax_unit("capital_gains_excluded_from_taxable_income", period)
            non_cg_taxable_income = max_(0, taxable_income - excluded_cg)
            income_less_ancg = max_(0, taxable_income - adjusted_net_cg)

            filing_status = tax_unit("filing_status", period)

            first_threshold = cg.thresholds["1"][filing_status]
            second_threshold = cg.thresholds["2"][filing_status]

            income_ordinarily_under_second_rate = clip(
                taxable_income, 0, first_threshold
            )

            income_ordinarily_under_third_rate = clip(
                taxable_income, 0, second_threshold
            )

            # The 2025 Biden Budget taxes the excess of long-term capital gains and qualified dividends
            # over $1 million as ordinary income.
            # We apply this only to ANCG, not Unrecaptured Section 1250 Gain or the 28% rate CG.

            p_reform = parameters(period).gov.contrib.biden.budget_2025.capital_gains
            income_threshold = p_reform.income_threshold[filing_status]
            # The threshold tests the filer's own income, which leaves out an
            # amount excluded under section 911, so it uses taxable income
            # before the excluded amount is added back; the rates still stack.
            excess_income = max_(
                0, tax_unit("taxable_income", period) - income_threshold
            )

            cg_in_top_bracket = min_(adjusted_net_cg, excess_income)

            income_tax = parameters(period).gov.irs.income.bracket.rates["7"]

            new_cg_tax = cg_in_top_bracket * income_tax

            cg_in_first_bracket = max_(
                0, income_ordinarily_under_second_rate - income_less_ancg
            )

            cg_in_first_bracket_below_top_bracket = max_(
                cg_in_first_bracket - cg_in_top_bracket, 0
            )

            cg_in_second_bracket = min_(
                max_(0, adjusted_net_cg - cg_in_first_bracket_below_top_bracket),
                max_(
                    0,
                    income_ordinarily_under_third_rate
                    - (non_cg_taxable_income + cg_in_first_bracket_below_top_bracket),
                ),
            )

            cg_in_second_bracket_below_top_bracket = max_(
                cg_in_second_bracket - cg_in_top_bracket, 0
            )

            cg_in_third_bracket = max_(
                adjusted_net_cg
                - cg_in_first_bracket_below_top_bracket
                - cg_in_second_bracket_below_top_bracket,
                0,
            )

            cg_in_third_bracket_below_top_bracket = max_(
                cg_in_third_bracket - cg_in_top_bracket, 0
            )

            main_cg_tax = (
                cg_in_first_bracket_below_top_bracket * cg.rates["1"]
                + cg_in_second_bracket_below_top_bracket * cg.rates["2"]
                + cg_in_third_bracket_below_top_bracket * cg.rates["3"]
                + new_cg_tax
            )

            unrecaptured_s_1250_gain = tax_unit(
                "section_911_unrecaptured_section_1250_gain", period
            )

            # Net capital gain determined without regard to section 1(h)(11),
            # reduced first by any capital gain excess (26 U.S.C.
            # 911(f)(2)(A)(i)).
            net_cg_other_than_dividends = (
                section_911_net_capital_gain_other_than_dividends(tax_unit, period)
            )
            max_taxable_unrecaptured_gain = min_(
                unrecaptured_s_1250_gain,
                net_cg_other_than_dividends,
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

            # As in the baseline formula, 28 percent of the rest of taxable
            # income (26 U.S.C. 1(h)(1)(F)): the 28 percent rate gain less
            # any of it taxed at the regular rates.
            remaining_cg_tax = cg.other_cg_rate * rate_gain_taxed_at_28_percent(
                tax_unit,
                period,
                taxable_income,
                non_cg_taxable_income,
                adjusted_net_cg,
                taxable_unrecaptured_gain,
            )
            # As in the baseline formula, section 1(h)(1) keeps the regular
            # tax within the tax on all taxable income at the main rates.
            return limit_to_tax_at_main_rates(
                tax_unit,
                period,
                main_cg_tax + unrecaptured_gain_tax + remaining_cg_tax,
            )

    class reform(Reform):
        def apply(self):
            self.update_variable(capital_gains_tax)

    return reform


def create_capital_gains_tax_increase_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_capital_gains_tax_increase()

    p = parameters(period).gov.contrib.biden.budget_2025.capital_gains

    if p.active:
        return create_capital_gains_tax_increase()
    else:
        return None


capital_gains_tax_increase = create_capital_gains_tax_increase_reform(
    None, None, bypass=True
)
