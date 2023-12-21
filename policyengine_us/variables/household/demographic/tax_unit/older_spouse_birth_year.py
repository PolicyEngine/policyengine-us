from policyengine_us.model_api import *


class older_spouse_birth_year(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    label = "Birth year of head or spouse of tax unit depending on which is greater"
    documentation = "Birth year of taxpayer (i.e. primary adult) or spouse (i.e. secondary adult if present), depending on which is greater. "
    unit = "year"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        birth_year = person("birth_year", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        # Set the value for dependents to .inf to avoid 0 values
        excluding_dependents_birth_year = where(
            head_or_spouse, birth_year, np.inf
        )
        return tax_unit.min(excluding_dependents_birth_year)
