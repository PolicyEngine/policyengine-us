from policyengine_us.model_api import *

RAILROAD_GROSS_INCOME_SOURCES = (
    "taxable_railroad_social_security_equivalent_benefits",
    "taxable_railroad_pension_benefits",
)


class taxable_railroad_benefits(Variable):
    value_type = float
    entity = Person
    label = "Railroad Retirement benefits in federal gross income"
    unit = USD
    documentation = (
        "The Railroad Retirement Act benefits that federal gross income "
        "includes for this person: the taxable tier 1 benefits treated as "
        "social security and the taxable rest of the annuity, counted as "
        "irs_gross_income counts them. 45 U.S.C. 231m(a) bars states from "
        "taxing these annuities, so states that start from federal adjusted "
        "gross income or taxable income subtract this amount."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/45/231m#a",
        "https://www.law.cornell.edu/uscode/text/26/86#d_1_B",
        "https://www.law.cornell.edu/uscode/text/26/72#r",
    )

    def formula(person, period, parameters):
        sources = parameters(period).gov.irs.gross_income.sources
        not_dependent = ~person("is_tax_unit_dependent", period)
        total = 0
        for source in RAILROAD_GROSS_INCOME_SOURCES:
            if source in sources:
                total += max_(0, person(source, period))
        return not_dependent * total
