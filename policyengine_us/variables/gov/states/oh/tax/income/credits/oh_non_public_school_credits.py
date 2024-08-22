from policyengine_us.model_api import *


class oh_non_public_school_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio Nonchartered, Nonpublic, School Tuition Credit AGI Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=21"
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.oh.tax.income.credits
        agi = tax_unit("adjusted_gross_income", period)
        person = tax_unit.members
        tuition = tax_unit.sum(person("non_public_school_tuition", period))
        cap = p.non_public_tuition.calc(agi)
        return min_(tuition, cap)
