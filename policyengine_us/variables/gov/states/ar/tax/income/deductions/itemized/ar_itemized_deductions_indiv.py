from policyengine_us.model_api import *


class ar_itemized_deductions_indiv(Variable):
    value_type = float
    entity = Person
    label = "Arkansas itemized deductions when married couples are filing separately"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR3_ItemizedDeduction.pdf"
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        # Arkansas does not tie itemization choice to federal choice.
        unit_deds = person.tax_unit("ar_itemized_deductions_unit", period)
        person_agi = person("ar_agi", period)
        total_agi = person.tax_unit.sum(person_agi)

        prorate = np.zeros_like(total_agi)
        mask = total_agi > 0
        prorate[mask] = person_agi[mask] / total_agi[mask]
        # Dependents should always return 0 as their AGI is always
        # attributed to the head of the tax unit in ar_agi
        return unit_deds * prorate
