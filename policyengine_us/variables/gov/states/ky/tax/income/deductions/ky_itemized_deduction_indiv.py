from policyengine_us.model_api import *


class ky_itemized_deductions_indiv(Variable):
    value_type = float
    entity = Person
    label = "Kentucky itemized deductions when married couples file separately"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.ky.gov/Forms/Form%20740%20Schedule%20A%202022.pdf"
        "https://law.justia.com/codes/kentucky/2022/chapter-141/section-141-019/"  # (2)(i)
    )
    defined_for = StateCode.KY

    def formula(person, period, parameters):
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        ky_agi = person("ky_agi", period) * head_or_spouse
        ky_agi_sum = person.tax_unit.sum(ky_agi)
        ky_agi_proportion = np.zeros_like(ky_agi_sum)
        mask = ky_agi_sum > 0
        ky_agi_proportion[mask] = ky_agi[mask] / ky_agi_sum[mask]
        itemized_deductions = person.tax_unit(
            "ky_itemized_deductions_unit", period
        )

        return ky_agi_proportion * itemized_deductions
