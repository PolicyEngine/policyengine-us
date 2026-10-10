from policyengine_us.model_api import *


class co_ctc_qualifying_child(Variable):
    value_type = bool
    entity = Person
    label = "Colorado child tax credit qualifying child"
    definition_period = YEAR
    reference = (
        # C.R.S. 39-22-129(2)(a) and (3.5)(a) - House Bill 23-1112.
        "https://leg.colorado.gov/sites/default/files/2023a_1112_signed.pdf#page=5",
        "https://www.law.cornell.edu/uscode/text/26/152#b_1",
    )
    defined_for = StateCode.CO

    def formula(person, period, parameters):
        age = person("age", period)
        p = parameters(period).gov.states.co.tax.income.credits.ctc
        is_dependent = person("is_tax_unit_dependent", period)
        # The 2022-2023 credit is a share of the federal child tax credit,
        # which is allowed only for the taxpayer's dependents. A return on
        # which the filer (or, if joint, either spouse) can be claimed as a
        # dependent has no dependents (IRC 152(b)(1)).
        filer_is_dependent = person.tax_unit(
            "head_or_spouse_is_dependent_elsewhere", period
        )
        return is_dependent & (age < p.age_threshold) & ~filer_is_dependent
