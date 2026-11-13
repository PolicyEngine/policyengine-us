from policyengine_us.model_api import *

# calculated by subtracting the resident credit, which is currently not modeled


class pa_eligibility_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "PA eligibility income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.pa.gov/content/dam/copapwp-pagov/en/revenue/documents/formsandpublications/formsforindividuals/pit/documents/2021/2021_pa-40sp.pdf"
    defined_for = StateCode.PA

    def formula(tax_unit, period, parameters):
        sources = parameters(
            period
        ).gov.states.pa.tax.income.forgiveness.eligibility_income_sources
        # The sources are amounts of the claimant and spouse; dependents file
        # their own PA return and their income is not part of the filer's
        # eligibility income.
        return tax_unit_non_dep_add(tax_unit, period, sources)
