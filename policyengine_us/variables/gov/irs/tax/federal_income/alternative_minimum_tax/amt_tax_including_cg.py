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
        # Form 6251 Part III, Line 12: AMTI minus exemption
        reduced_income = tax_unit("amt_income_less_exemptions", period)
        # Line 13: amount from QDCG Worksheet line 4 or Schedule D Tax
        # Worksheet line 13 (qualified dividends + LTCG net of unrecaptured
        # section 1250 and 28%-rate gains).
        cg_distributions = tax_unit("dwks13", period)
        # Line 14: Schedule D line 19 (unrecaptured section 1250 gain).
        section_1250_gain_worksheet = tax_unit("unrecaptured_section_1250_gain", period)
        # Line 15: smaller of (Line 13 + Line 14) or Schedule D Tax Worksheet
        # line 10.
        total_transactions_reported = tax_unit("dwks10", period)
        capped_capital_gains = min_(
            cg_distributions + section_1250_gain_worksheet,
            total_transactions_reported,
        )
        # Line 16: smaller of Line 12 or Line 15.
        capped_income = min_(capped_capital_gains, reduced_income)
        # Line 17: Line 12 minus Line 16 (ordinary AMTI).
        excess_income = max_(0, reduced_income - capped_income)
        # Line 18: apply the 26%/28% AMT bracket to Line 17.
        p = parameters(period).gov.irs
        income_taxes_at_amt_rates = p.income.amt.brackets.calc(excess_income)
        # Line 19: 0% LTCG bracket threshold for the filing status.
        filing_status = tax_unit("filing_status", period)
        cg_bracket = p.capital_gains.thresholds["1"][filing_status]
        # Line 20: amount from QDCG Worksheet line 5 or Schedule D Tax
        # Worksheet line 14 (as figured for the regular tax). This is the
        # ordinary-income portion of taxable income.
        regular_ordinary_income = tax_unit("dwks14", period)
        # Line 21: Line 19 minus Line 20. Room left in the 0% bracket after
        # accounting for ordinary income already filling it.
        reduced_cg_bracket = max_(0, cg_bracket - regular_ordinary_income)
        # Line 22: smaller of Line 12 or Line 13.
        smaller_of_income_or_cg = min_(reduced_income, cg_distributions)
        # Line 23: smaller of Line 21 or Line 22. This is the amount taxed at
        # 0% (not the tax — the form re-uses this amount in Line 24 and Line
        # 32, so we keep the quantity here rather than collapsing to the tax).
        amount_at_first_rate = min_(smaller_of_income_or_cg, reduced_cg_bracket)
        cg_first_rate = p.capital_gains.rates["1"]
        cg_first_bracket_tax = amount_at_first_rate * cg_first_rate
        # Line 24: Line 22 minus Line 23 (preferential-rate base remaining
        # after the 0% bracket).
        income_after_first_rate = max_(
            0, smaller_of_income_or_cg - amount_at_first_rate
        )
        # Line 25: 20% LTCG bracket threshold for the filing status.
        second_cg_bracket = p.capital_gains.thresholds["2"][filing_status]
        # Line 26: same as Line 21.
        # Line 27: amount from QDCG Worksheet line 5 or Schedule D Tax
        # Worksheet line 21 (as figured for the regular tax). For the QDCG
        # path this is the same ordinary-income value used on Line 20.
        # Line 28: Line 26 plus Line 27.
        first_cg_bracket_increased_by_ordinary = (
            reduced_cg_bracket + regular_ordinary_income
        )
        # Line 29: Line 25 minus Line 28 (room left in the 15% bracket).
        reduced_second_cg_bracket = max_(
            0, second_cg_bracket - first_cg_bracket_increased_by_ordinary
        )
        # Line 30: smaller of Line 24 or Line 29 (amount taxed at 15%).
        amount_at_second_rate = min_(income_after_first_rate, reduced_second_cg_bracket)
        # Line 31: Line 30 times the 15% LTCG rate.
        cg_second_bracket_tax = amount_at_second_rate * p.capital_gains.rates["2"]
        # Line 32: Line 23 plus Line 30 (cumulative preferential amounts).
        taxed_gains_amount = amount_at_first_rate + amount_at_second_rate
        # Line 33: Line 22 minus Line 32 (amount taxed at 20%).
        excess_taxed_gains = max_(0, smaller_of_income_or_cg - taxed_gains_amount)
        # Line 34: Line 33 times the 20% LTCG rate.
        cg_third_bracket_tax = excess_taxed_gains * p.capital_gains.rates["3"]
        # Line 35: Line 17 plus Line 32 plus Line 33.
        final_taxed_income = excess_income + taxed_gains_amount + excess_taxed_gains
        # Line 36: Line 12 minus Line 35 (unrecaptured section 1250 portion).
        final_excess = max_(0, reduced_income - final_taxed_income)
        # Line 37: Line 36 times the 25% rate, only when unrecaptured section
        # 1250 gains exist (per the form's "skip lines 35-37 if line 14 is
        # zero" instruction).
        unrecaptured_section_1250_gain = tax_unit(
            "unrecaptured_section_1250_gain", period
        )
        excess_tax = where(
            unrecaptured_section_1250_gain == 0,
            0,
            final_excess * p.income.amt.capital_gains.capital_gain_excess_tax_rate,
        )
        # Line 38: sum of Lines 18, 31, 34, and 37 (plus Line 23's 0%
        # contribution, which is always zero with a 0% bracket rate but kept
        # in the sum for structural clarity).
        return (
            income_taxes_at_amt_rates
            + cg_first_bracket_tax
            + cg_second_bracket_tax
            + cg_third_bracket_tax
            + excess_tax
        )
