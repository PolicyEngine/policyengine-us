from policyengine_us.model_api import *


class pr_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico adjusted gross income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.PR
    reference = (
        "https://hacienda.pr.gov/sites/default/files/individuals_2024_rev._jul_12_24_9-30-24_informative.pdf#page=2",
        "https://law.justia.com/codes/puerto-rico/title-thirteen/subtitle-17/part-ii/chapter-1005/subchapter-a/30103/",
    )

    # Discrepancy: legal code defines Puerto Rico AGI as gross income minus deductions and exemptions, among other items
    def formula(tax_unit, period, parameters):
        # person = tax_unit.members
        total_income = add(tax_unit, period, ["pr_gross_income_person"])
        alimony_paid = add(tax_unit, period, ["alimony_expense"])
        return max_(0, total_income - alimony_paid)
