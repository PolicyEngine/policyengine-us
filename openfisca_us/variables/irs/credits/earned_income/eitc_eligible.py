from openfisca_us.model_api import *


class eitc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for EITC"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/32#c_1_A"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        has_child = tax_unit.any(person("is_child", period))
        age = person("age", period)
        eitc = parameters(period).irs.credits.eitc
        meets_age_requirements = (age >= eitc.eligibility.age.min) & (
            age <= eitc.eligibility.age.max
        )
        return has_child | tax_unit.any(meets_age_requirements)
