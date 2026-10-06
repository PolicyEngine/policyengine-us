from policyengine_us.model_api import *


class nd_qdiv_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Dakota qualified dividends subtraction from federal taxable income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/form-nd-1-2021.pdf#page=1",  # line 13
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/individual-income-tax-booklet-2021.pdf#page=15",
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/form-nd-1-2022.pdf#page=1",  # line 13
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/2022-individual-income-tax-booklet.pdf#page=15",
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2025-iit/2025-individual-income-tax-booklet.pdf#page=15",  # line 13
        "https://ndlegis.gov/cencode/t57c38.pdf#nameddest=57-38-30p3",  # 2(d)(2)
    )
    defined_for = StateCode.ND

    def formula(tax_unit, period, parameters):
        # N.D.C.C. 57-38-30.3(2)(d)(2) reduces the individual's federal taxable
        # income by 40% of qualified dividends; Form ND-1 line 13 takes them
        # from Form 1040 line 3a. A tax unit dependent's dividends are on the
        # dependent's own return, so only the head's and spouse's count.
        qdiv = tax_unit_non_dep_add(tax_unit, period, ["qualified_dividend_income"])
        p = parameters(period).gov.states.nd.tax.income
        return qdiv * p.taxable_income.subtractions.qdiv_fraction
