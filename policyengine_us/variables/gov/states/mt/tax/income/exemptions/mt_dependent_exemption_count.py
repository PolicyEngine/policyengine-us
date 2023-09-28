from policyengine_us.model_api import *


class mt_dependent_exemption_count(Variable):
    value_type = float
    entity = TaxUnit
    label = "Number of Montana dependent exemptions"
    unit = USD
    definition_period = YEAR
    reference = "https://regulations.justia.com/states/montana/department-42/chapter-42-15/subchapter-42-15-4/rule-42-15-403/"
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        # Qualifying child under IRC 152(c), which defines for the EITC
        qualifying_child = person("is_eitc_qualifying_child", period)
        total_eligible = tax_unit.sum(qualifying_child)
        # Disabled dependents get an additional exemption.
        disabled = where(
            qualifying_child, person("is_disabled", period).astype(int), 0
        )
        total_disabled = tax_unit.sum(disabled)
        return total_eligible + total_disabled
