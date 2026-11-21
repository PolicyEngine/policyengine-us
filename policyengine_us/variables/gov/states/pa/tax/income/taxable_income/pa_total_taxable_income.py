from policyengine_us.model_api import *


class pa_total_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "PA total taxable income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.pa.gov/content/dam/copapwp-pagov/en/revenue/documents/formsandpublications/formsforindividuals/pit/documents/2021/2021_pa-40in.pdf#page=8",
        # PDF pages 4, 8, 12: minors file their own PA return even if claimed
        # as a dependent on a federal return (page 4); alimony is not taxable
        # (page 8); contributions to an employer-sponsored retirement plan are
        # PA-taxable compensation (page 12).
        "https://www.pa.gov/content/dam/copapwp-pagov/en/revenue/documents/formsandpublications/formsforindividuals/pit/documents/2025/2025_pa-40in.pdf#page=4",
    )
    defined_for = StateCode.PA

    def formula(tax_unit, period, parameters):
        us_gross_income = add(tax_unit, period, ["irs_gross_income"])
        other_additions = tax_unit("pa_other_additions", period)
        p = parameters(period).gov.states.pa.tax.income
        sources = p.nontaxable_income_sources
        # Federal gross income leaves out dependents' income; dependents file
        # their own PA return, so only the head's and spouse's elective
        # deferrals are added and only their nontaxable amounts subtracted.
        pa_taxable_deferrals = tax_unit_non_dep_add(
            tax_unit, period, ["pa_taxable_elective_deferrals"]
        )
        pa_nontaxable_income = tax_unit_non_dep_add(tax_unit, period, sources)
        return max_(
            0,
            us_gross_income
            + pa_taxable_deferrals
            + other_additions
            - pa_nontaxable_income,
        )
