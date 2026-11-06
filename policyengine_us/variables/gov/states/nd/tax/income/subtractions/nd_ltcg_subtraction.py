from policyengine_us.model_api import *


class nd_ltcg_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = (
        "North Dakota long-term capital gains subtraction from federal taxable income"
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/form-nd-1-2021.pdf#page=1",  # line 7
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/individual-income-tax-booklet-2021.pdf#page=14",
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/form-nd-1-2022.pdf#page=1",  # line 7
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/2022-individual-income-tax-booklet.pdf#page=14",
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2025-iit/2025-individual-income-tax-booklet.pdf#page=14",  # line 6
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2025-iit/2025-individual-income-tax-booklet.pdf#page=15",  # line 6 worksheet
        "https://ndlegis.gov/cencode/t57c38.pdf#nameddest=57-38-30p3",  # 2(d)(1)
    )
    defined_for = StateCode.ND

    def formula(tax_unit, period, parameters):
        # N.D.C.C. 57-38-30.3(2)(d)(1) reduces the individual's federal taxable
        # income by 40% of "the taxpayer's net long-term capital gain"; the
        # Form ND-1 line 6 worksheet takes it from the filer's Schedule D. A tax
        # unit dependent's gains are on the dependent's own return.
        # Worksheet line 1 is Schedule D line 15, the net long-term gain with
        # capital gain distributions, which are long-term (26 U.S.C.
        # 852(b)(3)(B)) and go on line 3 when there is no Schedule D. Line 2 is
        # Schedule D line 16, which adds the net short-term gain or loss. If
        # either is zero or less, no exclusion is allowed.
        long_term = tax_unit_non_dep_add(
            tax_unit, period, ["long_term_capital_gains"]
        ) + tax_unit_non_dep_add(tax_unit, period, ["non_sch_d_capital_gains"])
        short_term = tax_unit_non_dep_add(
            tax_unit, period, ["short_term_capital_gains"]
        )
        net_ltcg = max_(0, min_(long_term, long_term + short_term))
        p = parameters(period).gov.states.nd.tax.income
        return net_ltcg * p.taxable_income.subtractions.ltcg_fraction
