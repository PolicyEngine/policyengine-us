from openfisca_us.model_api import *


class ctc_eligible_children(Variable):
    value_type = int
    entity = TaxUnit
    label = "CTC-eligible children"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/24#c"

    def formula(tax_unit, period, parameters):
        ctc = parameters(period).irs.credits.child_tax_credit
        age = tax_unit.members("age", period)
        return tax_unit.sum(age <= ctc.eligibility.max_age)


class ctc_eligible_dependents(Variable):
    value_type = int
    entity = TaxUnit
    label = "ODC-eligible adult dependents"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/24#h_4"

    def formula(tax_unit, period, parameters):
        ctc = parameters(period).irs.credits.child_tax_credit
        person = tax_unit.members
        age = person("age", period)
        is_dependent = person("is_tax_unit_dependent", period)
        return tax_unit.sum(is_dependent & (age > ctc.eligibility.max_age))
