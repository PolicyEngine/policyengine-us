from policyengine_us.model_api import *


class oh_medicaid_child_has_other_creditable_coverage(Variable):
    value_type = bool
    entity = Person
    label = "Ohio Medicaid child has other creditable coverage"
    definition_period = YEAR
    defined_for = StateCode.OH
    reference = (
        "https://codes.ohio.gov/ohio-administrative-code/rule-5160:1-1-01",
        "https://codes.ohio.gov/ohio-administrative-code/rule-5160:1-4-02",
    )
    documentation = (
        "Uses the listed employer and individual insurance fields and modeled "
        "Medicare enrollment. Supply this input directly when a child has other "
        "qualifying coverage. "
        "Ohio Medicaid and its CHIP-funded expansion are the coverage being tested."
    )

    def formula(person, period, parameters):
        sources = parameters(period).gov.states.oh.odm.medicaid.child_coverage_sources
        return add(person, period, sources) > 0
