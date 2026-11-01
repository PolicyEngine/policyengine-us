from policyengine_us.model_api import *


class dependents_self_employed_health_insurance_ald(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit dependents' self-employed health insurance deductions"
    unit = USD
    documentation = (
        "The self-employed health insurance deductions (Schedule 1, line 17) of the tax "
        "unit's dependents, which belong on the dependents' own returns and "
        "are left out of self_employed_health_insurance_ald. For state "
        "income definitions that count dependents' income."
    )
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        is_dependent = person("is_tax_unit_dependent", period)
        amount = person("self_employed_health_insurance_ald_person", period)
        return tax_unit.sum(is_dependent * amount)
