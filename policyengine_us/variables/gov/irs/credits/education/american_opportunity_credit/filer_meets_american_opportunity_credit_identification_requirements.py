from policyengine_us.model_api import *


class filer_meets_american_opportunity_credit_identification_requirements(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Filer meets American Opportunity Credit identification requirements"
    definition_period = YEAR
    reference = "https://uscode.house.gov/view.xhtml?edition=prelim&num=0&req=granuleid%3AUSC-prelim-title26-section25A"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        meets_identification_requirements = person(
            "meets_american_opportunity_credit_identification_requirements",
            period,
        )
        return tax_unit.all(~head_or_spouse | meets_identification_requirements)
