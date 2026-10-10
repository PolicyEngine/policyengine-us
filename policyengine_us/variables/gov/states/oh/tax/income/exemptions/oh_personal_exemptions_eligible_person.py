from policyengine_us.model_api import *


class oh_personal_exemptions_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for the Ohio Exemption Credit"
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=14",
    )
    defined_for = StateCode.OH

    def formula(person, period, parameters):
        # The personal exemption is provided for the head and spouse
        # if they are not claimed as a dependent elsewhere
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        dependent_on_another_return = person(
            "claimable_as_dependent_on_another_return", period
        )
        # The personal exemption is also provided to dependents, but a return
        # on which the filer (or, if joint, either spouse) can be claimed as a
        # dependent has none (IRC 152(b)(1)).
        dependent_filer = person.tax_unit(
            "head_or_spouse_is_dependent_elsewhere", period
        )
        dependent = person("is_tax_unit_dependent", period) & ~dependent_filer
        return (~dependent_on_another_return & head_or_spouse) | dependent
