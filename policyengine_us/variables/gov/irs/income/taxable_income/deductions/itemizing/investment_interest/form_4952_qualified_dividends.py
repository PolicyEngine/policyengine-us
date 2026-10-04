from policyengine_us.model_api import *


class form_4952_qualified_dividends(Variable):
    value_type = float
    entity = TaxUnit
    label = "Form 4952 qualified dividends"
    unit = USD
    definition_period = YEAR
    documentation = """
    Form 4952 line 4b: "Qualified dividends included on line 4a". Sum only
    nondependent tax-unit members' qualified dividends, matching line 4a
    and the is_tax_unit_dependent exclusion in irs_gross_income and AGI.
    Under 163(d)(4)(B), qualified dividend income is investment income
    "only to the extent the taxpayer elects to treat such income as
    investment income"; line 4b removes it before line 4g's election.
    """
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/163#d_4_B",
        "https://www.irs.gov/pub/irs-pdf/f4952.pdf",
    ]

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        not_dependent = ~person("is_tax_unit_dependent", period)
        dividends = person("qualified_dividend_income", period)
        return tax_unit.sum(dividends * not_dependent)
