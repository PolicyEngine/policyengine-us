from policyengine_us.model_api import *


class ctc_child_individual_maximum(Variable):
    value_type = float
    entity = Person
    label = "CTC maximum amount (child)"
    unit = USD
    documentation = "The CTC entitlement in respect of this person as a child."
    definition_period = YEAR
    defined_for = "is_tax_unit_dependent"
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/24#a",
        "https://www.law.cornell.edu/uscode/text/26/24#h",
        "https://www.law.cornell.edu/uscode/text/26/24#i",
    )

    def formula(person, period, parameters):
        age = person("age", period)
        qualifying_child = person("ctc_qualifying_child", period)
        filer_meets_child_ctc_id_requirements = person.tax_unit(
            "filer_meets_child_ctc_identification_requirements", period
        )
        p = parameters(period).gov.irs.credits.ctc.amount
        return (
            qualifying_child * filer_meets_child_ctc_id_requirements * p.base.calc(age)
        )
