from policyengine_us.model_api import *

# calculated by subtracting the resident credit, which is currently not modeled


class pa_eligibility_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "PA eligibility income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.pa.gov/content/dam/copapwp-pagov/en/revenue/documents/formsandpublications/formsforindividuals/pit/documents/2021/2021_pa-40sp.pdf",
        "https://www.pa.gov/en/agencies/revenue/forms-and-publications/pa-personal-income-tax-guide/tax-forgiveness.html",
    )
    defined_for = StateCode.PA

    def formula(tax_unit, period, parameters):
        # Eligibility income is the claimant's, and the spouse's for a married
        # claimant; a dependent child claims forgiveness on their own return
        # (PA Personal Income Tax Guide, Tax Forgiveness). So only the head's
        # and spouse's amounts count.
        p = parameters(period).gov.states.pa.tax.income.forgiveness
        return tax_unit_non_dep_add(tax_unit, period, p.eligibility_income_sources)
