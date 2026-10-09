from policyengine_us.model_api import *


class me_dependent_exemption_credit_amount_person(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Maine dependent exemption credit amount for each person"
    reference = (
        "https://www.mainelegislature.org/legis/statutes/36/title36sec5219-SS.html"
    )
    definition_period = YEAR
    defined_for = "is_tax_unit_dependent"

    def formula(person, period, parameters):
        dependent = person("is_tax_unit_dependent", period)
        # 36 MRSA 5219-SS counts each "qualifying child and dependent" for
        # whom the taxpayer is eligible to claim the federal child tax credit
        # or credit for other dependents; a return on which the filer (or, if
        # joint, either spouse) can be claimed as a dependent has no
        # dependents (IRC 152(b)(1)).
        dependent_filer = person.tax_unit(
            "head_or_spouse_is_dependent_elsewhere", period
        )
        dependent = dependent & ~dependent_filer
        p = parameters(period).gov.states.me.tax.income.credits.dependent_exemption
        age = person("age", period)
        multiplier = p.multiplier.calc(age)
        return dependent * multiplier * p.amount
