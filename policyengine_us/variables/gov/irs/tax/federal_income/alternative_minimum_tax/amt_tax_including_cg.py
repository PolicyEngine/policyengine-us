from policyengine_us.model_api import *


class amt_tax_including_cg(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Alternative Minimum Tax computed using the capital gains rates"
    unit = USD
    documentation = "Alternative Minimum Tax (AMT) liability computed using the capital gains rates, Form 6251, Part III"
    reference = "https://www.irs.gov/pub/irs-pdf/f6251.pdf"

    def formula(tax_unit, period, parameters):
        # Line 12
        reduced_income = tax_unit("amt_income_less_exemptions", period)
        # Line 13 - schedule D line 13
        cg_distributions = tax_unit("dwks13", period)
        # Line 14 - schedule D line 19
        section_1250_gain_worksheet = tax_unit(
            "unrecaptured_section_1250_gain", period
        )
        # Line 15 - smaller of the sum of Line 13 and Line 14 or Schedule D line 10
        total_transactions_reported = tax_unit("dwks10", period)
        capped_capital_gains = min_(
            cg_distributions + section_1250_gain_worksheet,
            total_transactions_reported,
        )
        # Line 16 - smaller of Line 15 or Line 12
        capped_income = min_(capped_capital_gains, reduced_income)
        # Line 17 - Line 12 minus Line 16
        excess_income = max_(0, reduced_income - capped_income)
        # Line 18 - Apply CG tax rates to Line 17
        p = parameters(period).gov.irs
        income_taxes_at_amt_rates = p.income.amt.brackets.calc(excess_income)
        # Line 19 - First CG tax bracket threshold
        filing_status = tax_unit("filing_status", period)
        cg_bracket = p.capital_gains.brackets.thresholds["1"][filing_status]
        # Line 20 - Schedule D Line 14
        lt_capital_loss_carryover = tax_unit("dwks14", period)
        # Line 21 - Line 20 minus Line 19
        reduced_cg_bracket = max_(0, cg_bracket - lt_capital_loss_carryover)
        # Line 22 - smaller of Line 12 or Line 13
        smaller_of_income_or_cg = min_(reduced_income, cg_distributions)
        # Line 23 - smaller of Line 22 or Line 21 (amount is taxed at 0%)
        cg_first_rate = p.capital_gains.brackets.rates["1"]
        disregarded_gains = (
            min_(smaller_of_income_or_cg, reduced_cg_bracket) * cg_first_rate
        )
        # Line 24 - Line 22 minus Line 23
        taxable_income_including_cg = max_(
            smaller_of_income_or_cg - disregarded_gains, 0
        )
        # Line 25 - Second CG tax bracket threshold
        second_cg_bracket = p.capital_gains.brackets.thresholds["2"][
            filing_status
        ]
        # Line 26 - same as line 21
        # Line 27 - Schedule D Line 21
        loss_limited_net_capital_gains = tax_unit(
            "loss_limited_net_capital_gains", period
        )
        # Line 28 - Line 26 plus Line 27
        first_cg_bracket_increased_by_loss = (
            loss_limited_net_capital_gains + reduced_cg_bracket
        )
        # Line 29 Line 25 minus Line 28
        reduced_second_cg_bracket = max_(
            0, second_cg_bracket - first_cg_bracket_increased_by_loss
        )
        # Line 30 - smaller of Line 24 or Line 29
        capped_income_including_cg = min_(
            taxable_income_including_cg, reduced_second_cg_bracket
        )
        # Line 31 - multiply Line 30by second CG tax rate
        cg_second_bracket_tax = (
            capped_income_including_cg * p.capital_gains.brackets.rates["2"]
        )
        # Line 32 - Line 23 plus Line 30
        taxed_gains = disregarded_gains + capped_income_including_cg
        # Line 33 - Line 22 minus Line 32
        excess_taxed_gains = max_(0, smaller_of_income_or_cg - taxed_gains)
        # Line 34 - multiply Line 33 by third CG tax rate
        cg_third_bracket_tax = (
            excess_taxed_gains * p.capital_gains.brackets.rates["3"]
        )
        # Line 35 - sum of Line 17, Line 32, Line 33
        final_taxed_income = excess_income + taxed_gains + excess_taxed_gains
        # Line 36 Line 12 minus Line 35
        final_excess = max_(0, reduced_income - final_taxed_income)
        # Line 37 - Multiply Line 36 by the AMT specific capital gain excess tax rate
        # The increased tax does not applied if no recaptured section 1250 gains
        unrecaptured_section_1250_gain = tax_unit(
            "unrecaptured_section_1250_gain", period
        )
        excess_tax = where(
            unrecaptured_section_1250_gain == 0,
            0,
            final_excess
            * p.income.amt.capital_gains.capital_gain_excess_tax_rate,
        )
        # Line 38 - sum of Line 18, Line 31, Line 34, and Line 37
        return (
            income_taxes_at_amt_rates
            + cg_second_bracket_tax
            + cg_third_bracket_tax
            + excess_tax
        )
