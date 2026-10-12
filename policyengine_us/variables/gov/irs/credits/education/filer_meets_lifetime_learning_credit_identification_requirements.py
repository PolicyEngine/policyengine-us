from policyengine_us.model_api import *


class filer_meets_lifetime_learning_credit_identification_requirements(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Filer meets Lifetime Learning Credit identification requirements"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/25A#g_1"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        meets_identification_requirements = person(
            "meets_lifetime_learning_credit_identification_requirements",
            period,
        )
        return tax_unit.all(~head_or_spouse | meets_identification_requirements)
