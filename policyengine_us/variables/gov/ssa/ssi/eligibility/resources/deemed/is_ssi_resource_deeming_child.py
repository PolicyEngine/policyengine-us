from policyengine_us.model_api import *


class is_ssi_resource_deeming_child(Variable):
    value_type = bool
    entity = Person
    label = "Child subject to parental SSI resource deeming"
    definition_period = MONTH
    reference = (
        "https://www.ecfr.gov/current/title-20/section-416.1202#p-416.1202(b)",
        "https://www.ecfr.gov/current/title-20/section-416.1856",
        "https://www.ecfr.gov/current/title-20/section-416.1167",
        "https://secure.ssa.gov/poms.nsf/lnx/0501330200",
    )

    def formula(person, period, parameters):
        # 416.1856: 'You are not married' and 'not the head of a household'.
        # A two-person marital unit represents married, cohabiting spouses.
        # age is annual in the model: supply the relevant attained age.
        return (
            person("is_ssi_aged_blind_disabled", period)
            & (person("age", period.this_year) < 18)
            & (person.marital_unit.nb_persons() == 1)
            & ~person("is_household_head", period)
            & ~(
                person("ssi_lives_in_medical_treatment_facility", period)
                & ~person("ssi_resource_deeming_temporary_absence", period)
            )
            & ~person("ssi_resource_deeming_waiver", period)
            & ~person("ssi_resource_deeming_child_is_ineligible", period)
        )
