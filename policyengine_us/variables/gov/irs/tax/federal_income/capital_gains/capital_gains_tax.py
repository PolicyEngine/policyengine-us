from numpy import clip
from policyengine_us.model_api import *


class capital_gains_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maximum income tax after capital gains tax"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        net_cg = tax_unit("net_capital_gain", period)
        taxable_income = tax_unit("taxable_income", period)
        adjusted_net_cg = min_(
            tax_unit("adjusted_net_capital_gain", period),
            taxable_income,
        )  # ANCG is referred to in all cases as ANCG or taxable income if less.

        cg = parameters(period).gov.irs.capital_gains

        excluded_cg = tax_unit(
            "capital_gains_excluded_from_taxable_income", period
        )
        non_cg_taxable_income = max_(0, taxable_income - excluded_cg)
        income_less_ancg = max_(0, taxable_income - adjusted_net_cg)

        filing_status = tax_unit("filing_status", period)

        first_threshold = cg.brackets.thresholds["1"][filing_status]
        second_threshold = cg.brackets.thresholds["2"][filing_status]

        income_ordinarily_under_second_rate = clip(
            taxable_income, 0, first_threshold
        )
        cg_in_first_bracket = max_(
            0, income_ordinarily_under_second_rate - income_less_ancg
        )

        income_ordinarily_under_third_rate = clip(
            taxable_income, 0, second_threshold
        )
        cg_in_second_bracket = min_(
            max_(0, adjusted_net_cg - cg_in_first_bracket),
            max_(
                0,
                income_ordinarily_under_third_rate
                - (non_cg_taxable_income + cg_in_first_bracket),
            ),
        )

        cg_in_third_bracket = max_(
            adjusted_net_cg - cg_in_first_bracket - cg_in_second_bracket,
            0,
        )

        main_cg_tax = (
            cg_in_first_bracket * cg.brackets.rates["1"]
            + cg_in_second_bracket * cg.brackets.rates["2"]
            + cg_in_third_bracket * cg.brackets.rates["3"]
        )

        unrecaptured_s_1250_gain = tax_unit(
            "unrecaptured_section_1250_gain", period
        )
        qualified_dividends = add(
            tax_unit, period, ["qualified_dividend_income"]
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
        )

        return main_cg_tax + unrecaptured_gain_tax + remaining_cg_tax
