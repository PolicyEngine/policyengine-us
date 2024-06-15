from policyengine_us.model_api import *

"""
['adjusted_gross_income',
 'alternative_minimum_tax',
 'business_net_losses',
 'business_net_profits',
 'capital_gains_distributions',
 'capital_gains_gross',
 'capital_gains_losses',
 'charitable_contributions_deductions',
 'count',
 'employment_income',
 'estate_income',
 'estate_losses',
 'exempt_interest',
 'exemptions',
 'federal_tax_after_credits',
 'federal_tax_before_credits',
 'interest_paid_deductions',
 'ira_distributions',
 'itemized_deductions',
 'medical_expense_deductions_(capped)',
 'medical_expense_deductions_(uncapped)',
 'mortgage_interest_deductions',
 'ordinary_dividends',
 'partnership_and_s_corp_income',
 'partnership_and_s_corp_losses',
 'partnership_net_income',
 'partnership_net_losses',
 'qualified_business_income_deduction',
 'qualified_dividends',
 'rent_and_royalty_net_income',
 'rent_and_royalty_net_losses',
 's_corporation_net_income',
 's_corporation_net_losses',
 'standard_deduction',
 'state_and_local_tax_deductions',
 'taxable_interest_income',
 'taxable_pension_income',
 'taxable_social_security',
 'total_income',
 'total_pension_income',
 'total_social_security',
 'unemployment_compensation',
 'unknown']
"""


class irs_soi_adjusted_gross_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "adjusted gross income"
    unit = USD
    definition_period = YEAR
    adds = ["adjusted_gross_income"]


class irs_soi_alternative_minimum_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "alternative minimum tax"
    unit = USD
    definition_period = YEAR
    adds = ["alternative_minimum_tax"]


class irs_soi_business_net_losses(Variable):
    value_type = float
    entity = TaxUnit
    label = "business net losses"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        business_income = add(tax_unit, period, ["self_employment_income"])
        return max_(0, -business_income)


class irs_soi_business_net_profits(Variable):
    value_type = float
    entity = TaxUnit
    label = "business net profits"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        business_income = add(tax_unit, period, ["self_employment_income"])
        return max_(0, business_income)


class irs_soi_capital_gains_distributions(Variable):
    value_type = float
    entity = TaxUnit
    label = "capital gains distributions"
    unit = USD
    definition_period = YEAR
    adds = ["capital_gains"]


class irs_soi_capital_gains_gross(Variable):
    value_type = float
    entity = TaxUnit
    label = "capital gains gross"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        capital_gains = add(tax_unit, period, ["capital_gains"])

        return max_(0, capital_gains)


class irs_soi_capital_gains_losses(Variable):
    value_type = float
    entity = TaxUnit
    label = "capital gains losses"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        capital_gains = add(tax_unit, period, ["capital_gains"])

        return max_(0, -capital_gains)


class irs_soi_charitable_contributions_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "charitable contributions deductions"
    unit = USD
    definition_period = YEAR
    adds = ["charitable_deduction"]


class irs_soi_employment_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "employment income"
    unit = USD
    definition_period = YEAR
    adds = ["employment_income"]


class irs_soi_exempt_interest(Variable):
    value_type = float
    entity = TaxUnit
    label = "exempt interest"
    unit = USD
    definition_period = YEAR
    adds = ["tax_exempt_interest_income"]


class irs_soi_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "exemptions"
    unit = USD
    definition_period = YEAR
    adds = ["exemptions"]


class irs_soi_ira_distributions(Variable):
    value_type = float
    entity = TaxUnit
    label = "IRA distributions"
    unit = USD
    definition_period = YEAR
    adds = ["taxable_ira_distributions"]


class irs_soi_ordinary_dividends(Variable):
    value_type = float
    entity = TaxUnit
    label = "ordinary dividends"
    unit = USD
    definition_period = YEAR
    adds = ["dividend_income"]


class irs_soi_qualified_dividends(Variable):
    value_type = float
    entity = TaxUnit
    label = "qualified dividends"
    unit = USD
    definition_period = YEAR
    adds = ["qualified_dividend_income"]
