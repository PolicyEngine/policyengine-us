from policyengine_us.model_api import *


class az_property_tax_credit_nontaxable_income(Variable):
    value_type = float
    entity = Person
    label = "Arizona property tax credit income left out of federal gross income"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Strike benefits and alimony received that federal gross income leaves "
        "out, which Arizona household income counts for every household "
        "member: nontaxable strike benefits (ARS 43-1072(H)(6)(c); Form "
        "140PTC line I) and all alimony received (line H). Only the part of "
        "each that federal gross income does not already hold is added, so "
        "nothing counts twice."
    )
    reference = [
        "https://www.azleg.gov/ars/43/01072.htm",  # ARS 43-1072(H)(5), (H)(6)
        "https://azdor.gov/sites/default/files/document/FORMS_INDIVIDUAL_2025_140PTCi.pdf#page=4",
    ]
    defined_for = StateCode.AZ

    def formula(person, period, parameters):
        sources = parameters(period).gov.irs.gross_income.sources
        # Federal gross income (irs_gross_income for members who are not
        # dependents, the same sources in az_property_tax_credit_dependent_income
        # for dependents) holds strike benefits only if they are a listed source.
        strike = person("strike_benefits", period)
        excluded_strike = 0 if "strike_benefits" in sources else strike
        # Line H counts "all alimony received by each member of the household";
        # federal gross income holds taxable_alimony_income (alimony under
        # pre-2019 divorce instruments).
        alimony = person("alimony_income", period)
        if "taxable_alimony_income" in sources:
            taxable_alimony = person("taxable_alimony_income", period)
            excluded_alimony = max_(alimony - taxable_alimony, 0)
        else:
            excluded_alimony = alimony
        return excluded_strike + excluded_alimony
