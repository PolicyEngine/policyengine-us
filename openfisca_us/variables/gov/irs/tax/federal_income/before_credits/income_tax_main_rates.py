from openfisca_us.model_api import *


class c05200(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Income tax main rates"
    reference = "https://www.law.cornell.edu/uscode/text/26/1"
    unit = USD

    def formula(tax_unit, period, parameters):
        # Separate non-negative taxable income into two non-negative components,
        # doing this in a way so that the components add up to taxable income
        # define pass-through income eligible for PT schedule
        individual_income = parameters(period).gov.irs.income
        e26270 = add(tax_unit, period, ["partnership_s_corp_income"])
        e00900 = add(tax_unit, period, ["self_employment_income"])

        # Determine pass-through and non-pass-through income
        pt_active_gross = e00900 + e26270
        pt_active = pt_active_gross
        pt_active = min_(pt_active, e00900 + e26270)
        pt_taxinc = max_(0, pt_active)
        full_taxable_income = tax_unit("taxable_income", period)

        # 1(h) describes a mechanism for capital gains tax that caps income tax
        # at an amount which includes 'as if income tax rates were applied on taxable
        # income excluding some definiton of capital gains'. Instead of calculating
        # both income tax and this hypothetical income tax, we'll just calculate the latter.

        cg_exclusion = tax_unit(
            "capital_gains_excluded_from_taxable_income", period
        )
        taxable_income = max_(0, full_taxable_income - cg_exclusion)

        pt_taxinc = min_(pt_taxinc, taxable_income)
        reg_taxinc = max_(0, taxable_income - pt_taxinc)
        pt_tbase = reg_taxinc

        filing_status = tax_unit("filing_status", period)

        # Initialise regular and pass-through income tax to zero
        reg_tax = 0
        pt_tax = 0
        last_reg_threshold = 0
        last_pt_threshold = 0
        for i in range(1, 7):
            # Calculate rate applied to regular income up to the current
            # threshold (on income above the last threshold)
            reg_threshold = individual_income.bracket.thresholds[str(i)][
                filing_status
            ]
            reg_tax += individual_income.bracket.rates[
                str(i)
            ] * amount_between(reg_taxinc, last_reg_threshold, reg_threshold)
            last_reg_threshold = reg_threshold

            # Calculate rate applied to pass-through income on in the same
            # way, but as treated as if stacked on top of regular income
            # (which is not taxed again)
            pt_threshold = max_(
                0,
                individual_income.pass_through.bracket.thresholds[str(i)][
                    filing_status
                ]
                - pt_tbase,
            )
            pt_tax += individual_income.pass_through.bracket.rates[
                str(i)
            ] * amount_between(pt_taxinc, last_pt_threshold, pt_threshold)
            last_pt_threshold = pt_threshold

        # Calculate regular and pass-through tax above the last threshold
        reg_tax += individual_income.bracket.rates["7"] * max_(
            reg_taxinc - last_reg_threshold, 0
        )
        pt_tax += individual_income.pass_through.bracket.rates["7"] * max_(
            pt_taxinc - last_pt_threshold, 0
        )
        return reg_tax + pt_tax


income_tax_main_rates = variable_alias("income_tax_main_rates", c05200)
