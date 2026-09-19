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
        receives_ssi = (person("ssi", period) > 0) | person("receives_ssi", period)
        federal_la = person("ssi_federal_living_arrangement", period)
        in_medical_facility = (
            federal_la == SSIFederalLivingArrangement.MEDICAL_TREATMENT_FACILITY
        )
        # SSPP goes to SSI recipients, who are Medicaid eligible under
        # 42 U.S.C. 1396a(a)(10)(A)(i)(II) and so fall outside the subclause
        # (VIII) adult group, the only group the community engagement
        # requirement applies to (1396a(xx)(9)(A)(i)). Reading Medicaid
        # enrollment before work requirements is therefore exact, and it
        # keeps this payment out of the Medicaid -> SNAP -> state supplement
        # cycle that opens in 2027 (issue #9534).
        on_medicaid = person(
            "medicaid_enrolled_before_work_requirements", period.this_year
        )
        age = person("age", period.this_year)
        return (
            receives_ssi & in_medical_facility & on_medicaid & (age >= p.age_threshold)
        )
