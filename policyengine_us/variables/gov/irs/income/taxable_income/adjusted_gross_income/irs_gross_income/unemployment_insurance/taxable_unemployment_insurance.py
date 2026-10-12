from policyengine_us.model_api import *


class taxable_unemployment_compensation(Variable):
    value_type = float
    entity = Person
    label = "Taxable unemployment compensation"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        # The taxable amount of unemployment compensation is decided at the tax
        # unit level, but gross income (which contains taxable UI) is person-level.
        # Allocate the tax unit's taxable UC to each person in proportion to their
        # unemployment_compensation, so that per-person AGI reflects the actual
        # recipient (required by states with combined-return optimization).
        tax_unit_taxable_uc = person.tax_unit(
            "tax_unit_taxable_unemployment_compensation", period
        )
        person_uc = person("unemployment_compensation", period)
        tax_unit_uc = person.tax_unit.sum(person_uc)
        share = where(tax_unit_uc > 0, person_uc / tax_unit_uc, 0)
        return tax_unit_taxable_uc * share
