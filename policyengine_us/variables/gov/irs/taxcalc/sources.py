from policyengine_us.model_api import *


class f6251(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        "True if Form 6251 (AMT) attached to return; otherwise false"
    )


class a_lineno(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    documentation = "CPS line number for the person record of the head of the tax filing unit (not used in tax-calculation logic)"


class ffpos(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    documentation = "CPS family identifier within household (not used in tax-calculation logic)"


class fips(Variable):
    value_type = int
    entity = Household
    definition_period = YEAR
    documentation = "FIPS state code (not used in tax-calculation logic)"
    default_value = 6


class h_seq(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        "CPS household sequence number (not used in tax-calculation logic)"
    )


class data_source(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    documentation = "True if unit is created primarily from IRS-SOI PUF data; false if created primarily from CPS data (not used in tax-calculation logic)"


class k1bx14(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = (
        "Partner self-employment earnings/loss (included in e26270 total)"
    )
    unit = USD


class filer_k1bx14(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Partner self-employment earnings/loss for tax unit (excluding dependents) (included in e26270 total)"
    unit = USD

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("k1bx14", tax_unit, period)


class n24(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Number of children who are Child-Tax-Credit eligible, one condition for which is being under age 17"


class nu06(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Number of dependents under 6 years old"


class nu13(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Number of dependents under 13 years old"


class nu18(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Number of people under 18 years old in the filing unit"


class n1820(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Number of people age 18-20 years old in the filing unit"


class n21(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Number of people 21 years old or older in the filing unit"


class hasqdivltcg(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Has qualified dividends or long-term capital gains"
    documentation = "Whether this tax unit has qualified dividend income, or long-term capital gains income"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        # Negatives cannot offset other income sources
        INCOME_SOURCES = [
            "c01000",
            "c23650",
            "long_term_capital_gains",
            "non_sch_d_capital_gains",
            "qualified_dividend_income",
        ]
        return np.any(
            [
                add(tax_unit, period, [income_source]) > 0
                for income_source in INCOME_SOURCES
            ]
        )


class c23650(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Net capital gains"
    unit = USD
    documentation = "Net capital gains (long and short term) before exclusion"

    def formula(tax_unit, period, parameters):
        return add(
            tax_unit,
            period,
            ["long_term_capital_gains", "short_term_capital_gains"],
        )
