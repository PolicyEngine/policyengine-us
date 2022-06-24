from openfisca_us.model_api import *


class cmbtp(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "AMT income not included in AGI"
    documentation = "Estimate of income considered for AMT but not AGI"
    unit = USD


class filer_cmbtp(Variable):
    value_type = float
    entity = TaxUnit
    label = "Income on Form 6251 not in AGI for the tax unit (excluding dependents)"
    definition_period = YEAR
    unit = USD

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("cmbtp", tax_unit, period)


class e00200(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = "Wages, salaries, and tips net of pension contributions"
    unit = USD

    def formula(person, period, parameters):
        return person("employment_income", period)


class filer_e00200(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Wages, salaries, and tips for filing unit (excluding dependents) net of pension contributions (pencon)"
    unit = USD

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("e00200", tax_unit, period)


class pencon(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = "Contributions to defined-contribution pension plans"
    unit = USD


class filer_pencon(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Contributions to defined-contribution pension plans for filing unit (excluding dependents)"
    unit = USD

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("pencon", tax_unit, period)


class e00300(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = "Taxable interest income"
    unit = USD

    def formula(person, period, parameters):
        return person("interest_income", period)


class filer_e00300(Variable):
    value_type = float
    entity = TaxUnit
    label = "Taxable interest income for the tax unit (excluding dependents)"
    definition_period = YEAR
    unit = USD

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("e00300", tax_unit, period)


class e02300(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = "Unemployment compensation benefits"
    unit = USD


class filer_e02300(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Unemployment compensation benefits for filing unit (excluding dependents)"
    unit = USD

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum(
            "unemployment_compensation", tax_unit, period
        )


class e02400(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = "Total Social Security (OASDI) benefits"
    unit = USD

    def formula(person, period, parameters):
        return person("social_security", period)


class tax_unit_ss(Variable):
    value_type = float
    entity = TaxUnit
    label = "Social security benefits for the tax unit (excluding dependents)"
    definition_period = YEAR
    unit = USD

    def formula(tax_unit, period, parameters):
        return add(tax_unit, period, ["social_security"])


class e87530(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Qualified tuition expenses"
    documentation = (
        "Adjusted qualified lifetime learning expenses for all students"
    )
    unit = USD


class elderly_dependents(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Number of dependents age 65+ in filing unit excluding taxpayer and spouse"


class incapable_of_self_care(Variable):
    value_type = bool
    entity = Person
    label = "Incapable of self-care"
    documentation = "Whether this person is physically or mentally incapable of caring for themselves."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/21"


class cdcc_qualified_dependent(Variable):
    value_type = bool
    entity = Person
    label = "Qualifying dependent for CDCC"
    documentation = "Whether this person qualifies as a dependent for the child and dependent care credit."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/21"

    def formula(person, period, parameters):
        cdcc = parameters(period).gov.irs.credits.cdcc
        meets_age_criteria = person("age", period) < cdcc.eligibility.child_age
        incapable_of_self_care = person("incapable_of_self_care", period)
        is_dependent = person("is_tax_unit_dependent", period)
        is_spouse = person("is_tax_unit_spouse", period)
        dependent_or_spouse = is_dependent | is_spouse
        return meets_age_criteria | (
            dependent_or_spouse & incapable_of_self_care
        )


class f2441(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Number of child/dependent-care qualifying persons"

    def formula(tax_unit, period, parameters):
        gross_num_eligible = tax_unit.sum(
            tax_unit.members("cdcc_qualified_dependent", period)
        )
        cdcc = parameters(period).gov.irs.credits.cdcc
        return min_(gross_num_eligible, cdcc.eligibility.max)


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
