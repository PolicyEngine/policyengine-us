from policyengine_us.model_api import *


class medical_expense_health_insurance_premiums(Variable):
    value_type = float
    entity = Person
    label = "Health insurance premiums for medical expense definitions"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Person-level non-pretax health insurance premiums for medical expense "
        "definitions. Uses a nonzero direct health_insurance_premiums input; "
        "otherwise combines non-Medicare premiums with modeled Medicare Part B "
        "premiums for enrollees. Excludes the disjoint "
        "pre_tax_health_insurance_premiums input. Consumers whose rules count "
        "pretax payroll payments add that separate input once; tax deductions "
        "that exclude them use this aggregate alone."
    )

    def formula(person, period, parameters):
        direct = person("health_insurance_premiums", period)
        non_medicare = person(
            "health_insurance_premiums_without_medicare_part_b", period
        )
        medicare_enrolled = person("medicare_enrolled", period)
        medicare_part_b = person("medicare_part_b_premium", period) * medicare_enrolled
        decomposed = non_medicare + medicare_part_b
        return where(direct != 0, direct, decomposed)
