from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.status.ssi_federal_living_arrangement import (
    SSIFederalLivingArrangement,
)


class ks_sspp_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Kansas SSPP eligible"
    definition_period = MONTH
    defined_for = StateCode.KS
    reference = (
        "https://ksrevisor.gov/statutes/chapters/ch39/039_009_0072.html",
        "https://khap.kdhe.ks.gov/kfmam/policydocs/state%20supplemental%20payment%20program%20policy%20memo.pdf#page=2",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ks.kdhe.sspp.eligibility
        receives_ssi = person("ssi", period) > 0
        federal_la = person("ssi_federal_living_arrangement", period.this_year)
        in_medical_facility = (
            federal_la == SSIFederalLivingArrangement.MEDICAL_TREATMENT_FACILITY
        )
        on_medicaid = person("medicaid_enrolled", period.this_year)
        age = person("age", period.this_year)
        return (
            receives_ssi & in_medical_facility & on_medicaid & (age >= p.age_threshold)
        )
