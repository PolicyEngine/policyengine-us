from policyengine_us.model_api import *


class ne_refundable_ctc_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Nebraska refundable Child Tax Credit eligible child"
    definition_period = YEAR
    reference = (
        "https://nebraskalegislature.gov/laws/statutes.php?statute=77-7202",
        "https://revenue.nebraska.gov/businesses/child-care-tax-credit-act",
        "https://revenue.nebraska.gov/sites/default/files/doc/tax-forms/f_7203_instruction_only.pdf#page=1",
        "https://www.law.cornell.edu/uscode/text/26/152#b_1",
    )
    defined_for = StateCode.NE

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ne.tax.income.credits.ctc.refundable
        age_eligible = person("age", period) <= p.age_threshold
        is_dependent = person("is_tax_unit_dependent", period)
        # Neb. Rev. Stat. 77-7202 defines the parent or guardian as one who
        # "claims a child as a dependent for federal income tax purposes".
        # Under IRC 152(b)(1) a return on which the filer, or on a joint
        # return either spouse, can be claimed as a dependent has no
        # dependents.
        filer_is_dependent = person.tax_unit(
            "head_or_spouse_is_dependent_elsewhere", period
        )
        age_eligible_dependent = age_eligible & is_dependent & ~filer_is_dependent
        # Nebraska limits the CTC to children who are either:
        # 1) enrolled in a child care program licensed pursuant to the Child Care
        #    Licensing Act
        # 2) receiving care from an approved license-exempt provider enrolled in
        #    the child care subsidy program pursuant to Neb. Rev. Stat. §§ 68-1202
        #    and 68-1206
        # As we do not yet model licensure status or subsidy-program enrollment,
        # we approximate this gate as the tax unit having reported childcare
        # expenses — the same input used by the federal CDCC and every other
        # state dependent-care credit.
        received_qualifying_child_care = (
            person.tax_unit("tax_unit_childcare_expenses", period) > 0
        )
        income_eligible = person.tax_unit("ne_refundable_ctc_income_eligible", period)
        return age_eligible_dependent & (
            received_qualifying_child_care | income_eligible
        )
