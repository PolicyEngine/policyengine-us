from policyengine_us.model_api import *


label = "Income"


class employment_income(Variable):
    value_type = float
    entity = Person
    label = "employment income"
    documentation = "Wages and salaries, including tips and commissions."
    unit = USD
    definition_period = YEAR


class self_employment_income(Variable):
    value_type = float
    entity = Person
    label = "self-employment income"
    unit = USD
    documentation = "Self-employment non-farm income."
    definition_period = YEAR


class pension_income(Variable):
    value_type = float
    entity = Person
    label = "pension income"
    unit = USD
    documentation = "Income from pensions, annuitities, life insurance or endowment contracts."
    definition_period = YEAR
    adds = [
        "tax_exempt_pension_income",
        "taxable_pension_income",
    ]


class interest_income(Variable):
    value_type = float
    entity = Person
    label = "interest income"
    documentation = "Interest income from bonds, savings accounts, CDs, etc."
    unit = USD
    definition_period = YEAR
    adds = [
        "tax_exempt_interest_income",
        "taxable_interest_income",
    ]


class farm_income(Variable):
    value_type = float
    entity = Person
    label = "farm income"
    unit = USD
    documentation = "Income from agricultural businesses. Do not include this income in self-employment income."
    definition_period = YEAR


class dividend_income(Variable):
    value_type = float
    entity = Person
    label = "ordinary dividend income"
    documentation = "Qualified and non-qualified dividends"
    unit = USD
    definition_period = YEAR
    adds = [
        "qualified_dividend_income",
        "non_qualified_dividend_income",
    ]


class capital_gains(Variable):
    value_type = float
    entity = Person
    label = "capital gains"
    unit = USD
    documentation = "Net gain from disposition of property."
    definition_period = YEAR
    adds = [
        "short_term_capital_gains",
        "long_term_capital_gains",
    ]
