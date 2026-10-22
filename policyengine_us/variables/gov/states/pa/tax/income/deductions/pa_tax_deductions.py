from policyengine_us.model_api import *

# PA law does not allow standard deductions, deductions for personal exemptions, itemized deductions or deductions for personal expenses.
# However, PA does allow deductions for 529 plan contributions.


class pa_tax_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "PA deductions against taxable income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.pa.gov/content/dam/copapwp-pagov/en/revenue/documents/formsandpublications/formsforindividuals/pit/documents/2021/2021_pa-40in.pdf#page=20",
        "https://www.pa.gov/content/dam/copapwp-pagov/en/revenue/documents/formsandpublications/formsforindividuals/pit/documents/2025/2025_pa-40in.pdf#page=21",
    )
    defined_for = StateCode.PA

    def formula(tax_unit, period, parameters):
        deductions = add(
            tax_unit, period, ["pa_529_plan_deduction", "pa_other_subtractions"]
        )
        # PA-40 line 10 cannot exceed line 9, total PA taxable income.
        # The separate per-spouse limit on joint returns is not modeled.
        total_taxable_income = tax_unit("pa_total_taxable_income", period)
        return min_(deductions, total_taxable_income)
