from policyengine_us.model_api import *


class pa_total_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "PA total taxable income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.pa.gov/content/dam/copapwp-pagov/en/revenue/documents/formsandpublications/formsforindividuals/pit/documents/2021/2021_pa-40in.pdf#page=8",
        # Minors file their own PA return even if claimed as a dependent on
        # a federal return.
        "https://www.pa.gov/content/dam/copapwp-pagov/en/revenue/documents/formsandpublications/formsforindividuals/pit/documents/2025/2025_pa-40in.pdf#page=4",
    )
    defined_for = StateCode.PA

    def formula(tax_unit, period, parameters):
        us_gross_income = add(tax_unit, period, ["irs_gross_income"])
        p = parameters(period).gov.states.pa.tax.income
        sources = p.nontaxable_income_sources
        # The sources are amounts in federal gross income, which leaves out
        # dependents' income; dependents file their own PA return, so only
        # the head's and spouse's amounts are subtracted.
        pa_nontaxable_income = tax_unit_non_dep_add(tax_unit, period, sources)
        return max_(0, us_gross_income - pa_nontaxable_income)
