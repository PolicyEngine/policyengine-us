from policyengine_us.model_api import *


class in_ssp_sapn_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Indiana Supplemental Assistance for Personal Needs"
    definition_period = MONTH
    defined_for = StateCode.IN
    reference = (
        "https://www.in.gov/fssa/ompp/files/Medicaid_PM_5000.pdf",
        "https://secure.ssa.gov/poms.nsf/lnx/0501401001CHI",
    )

    def formula(person, period, parameters):
        # IC 12-15-32-6.5: must be "a recipient of assistance under the federal SSI program"
        is_ssi_recipient = (person("ssi", period) > 0) | person("receives_ssi", period)
        # SAPN goes to SSI recipients, who are Medicaid eligible under
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
        p = parameters(period).gov.states["in"].fssa.ssp
        age_eligible = age >= p.age_threshold
        arrangement = person("ssi_federal_living_arrangement", period)
        in_medicaid_facility = (
            arrangement == arrangement.possible_values.MEDICAL_TREATMENT_FACILITY
        )
        return is_ssi_recipient & on_medicaid & age_eligible & in_medicaid_facility
