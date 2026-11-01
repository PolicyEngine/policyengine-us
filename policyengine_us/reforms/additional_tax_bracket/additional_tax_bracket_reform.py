from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant
from policyengine_us.variables.gov.irs.tax.federal_income.before_credits.tax_at_main_rates import (
    amount_taxed_below_rate,
    tax_at_main_rates,
)


def create_additional_tax_bracket() -> Reform:
    class income_tax_main_rates(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "Income tax main rates"
        reference = [
            "https://www.law.cornell.edu/uscode/text/26/1",
            "https://www.law.cornell.edu/uscode/text/26/911#f_1_A",
        ]
        unit = USD

        def formula(tax_unit, period, parameters):
            # compute taxable income that is taxed at the main rates; as in
            # the baseline formula, a taxpayer excluding foreign earned
            # income adds the excluded amount back (26 U.S.C. 911(f)(1)(A))
            full_taxable_income = tax_unit(
                "taxable_income_plus_section_911_exclusion", period
            )
            cg_exclusion = tax_unit(
                "capital_gains_excluded_from_taxable_income", period
            )
            taxinc = max_(0, full_taxable_income - cg_exclusion)
            # compute tax using bracket rates and thresholds
            bracket = parameters(period).gov.contrib.additional_tax_bracket.bracket
            filing_status = tax_unit("filing_status", period)
            tax = tax_at_main_rates(taxinc, filing_status, bracket)
            # less the tax on the excluded amount alone
            excluded = max_(0, tax_unit("foreign_earned_income_exclusion", period))
            tax_on_excluded = tax_at_main_rates(excluded, filing_status, bracket)
            return where(excluded > 0, max_(0, tax - tax_on_excluded), tax)

    class tax_on_taxable_income_at_main_rates(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "Tax on all taxable income at the main rates"
        reference = "https://www.law.cornell.edu/uscode/text/26/1#h_1"
        unit = USD

        def formula(tax_unit, period, parameters):
            # Schedule D Tax Worksheet line 46 on the reform's rate schedule,
            # as in the baseline formula on the baseline schedule. Section
            # 1(h)(1) caps the regular tax at it (capital_gains_tax).
            taxable_income = tax_unit(
                "taxable_income_plus_section_911_exclusion", period
            )
            bracket = parameters(period).gov.contrib.additional_tax_bracket.bracket
            filing_status = tax_unit("filing_status", period)
            tax = tax_at_main_rates(max_(0, taxable_income), filing_status, bracket)
            excluded = max_(0, tax_unit("foreign_earned_income_exclusion", period))
            tax_on_excluded = tax_at_main_rates(excluded, filing_status, bracket)
            return where(excluded > 0, max_(0, tax - tax_on_excluded), tax)

    class taxable_income_taxed_below_25_percent(Variable):
        value_type = float
        entity = TaxUnit
        label = "Taxable income taxed at a rate below 25 percent"
        unit = USD
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/1#h_1_A_ii_I"

        def formula(tax_unit, period, parameters):
            # 26 U.S.C. 1(h)(1)(A)(ii)(I) on the reform's rate schedule, as
            # in the baseline formula on the baseline schedule.
            taxable_income = tax_unit(
                "taxable_income_plus_section_911_exclusion", period
            )
            filing_status = tax_unit("filing_status", period)
            return amount_taxed_below_rate(
                taxable_income,
                filing_status,
                parameters(period).gov.contrib.additional_tax_bracket.bracket,
                parameters(period).gov.irs.capital_gains.regular_rate_limit,
            )

    class reform(Reform):
        def apply(self):
            self.update_variable(income_tax_main_rates)
            self.update_variable(tax_on_taxable_income_at_main_rates)
            self.update_variable(taxable_income_taxed_below_25_percent)

    return reform


def create_additional_tax_bracket_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_additional_tax_bracket()

    p = parameters.gov.contrib.additional_tax_bracket

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_additional_tax_bracket()
    else:
        return None


additional_tax_bracket = create_additional_tax_bracket_reform(None, None, bypass=True)
