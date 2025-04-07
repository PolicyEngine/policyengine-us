from policyengine_us.model_api import *


class de_itemized_deductions_indv(Variable):
    value_type = float
    entity = Person
    label = "Delaware itemized deductions when married couples are filing separately"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenuefiles.delaware.gov/2022/TY22_PIT-RSA_2022-02_PaperInteractive.pdf",  # § 1109
        "https://delcode.delaware.gov/title30/c011/sc02/index.html",
    )
    defined_for = StateCode.DE

    def formula(person, period, parameters):
        unit_deds = person.tax_unit("de_itemized_deductions_unit", period)
        person_agi = person("adjusted_gross_income_person", period)
        total_agi = person.tax_unit.sum(person_agi)

        prorate = np.zeros_like(total_agi)
        mask = total_agi > 0
        prorate[mask] = person_agi[mask] / total_agi[mask]
        # Dependents should always return 0 as their AGI is always
        # attributed to the head of the tax unit in de_agi
        return unit_deds * prorate
