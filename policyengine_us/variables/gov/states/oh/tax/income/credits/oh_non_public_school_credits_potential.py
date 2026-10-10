from policyengine_us.model_api import *


class oh_non_public_school_credits_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio Nonchartered, Nonpublic, School Tuition Credit AGI Credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=21",
        "https://codes.ohio.gov/ohio-revised-code/section-5747.75",
        # 5747.01(O): "Dependents" means dependents as defined in the IRC.
        "https://codes.ohio.gov/ohio-revised-code/section-5747.01",
        "https://www.law.cornell.edu/uscode/text/26/152#b_1",
    )
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.oh.tax.income.credits
        agi = tax_unit("adjusted_gross_income", period)
        person = tax_unit.members
        # R.C. 5747.75 counts the tuition paid "for all of the taxpayer's
        # dependents", and 5747.01(O) takes dependents from the IRC, under
        # which a return on which the filer (or, if joint, either spouse) can
        # be claimed as a dependent has none (IRC 152(b)(1)).
        filer_is_dependent = person.tax_unit(
            "head_or_spouse_is_dependent_elsewhere", period
        )
        dependent = person("is_tax_unit_dependent", period) & ~filer_is_dependent
        tuition = tax_unit.sum(person("non_public_school_tuition", period) * dependent)
        cap = p.non_public_tuition.calc(agi)
        return min_(tuition, cap)
