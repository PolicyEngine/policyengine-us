from policyengine_us.model_api import *


class is_adult_for_medicaid_nfc(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid adult non-financial criteria"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/42/435.119",
        "https://www.law.cornell.edu/uscode/text/42/1396a#a_10_A_i_VIII",
        "https://dssmanuals.mo.gov/family-mo-healthnet-magi/1865-000-00/1865-020-00/",
    )

    def formula(person, period, parameters):
        ma = parameters(period).gov.hhs.medicaid.eligibility.categories.adult
        age = person("age", period)
        age_eligible = ma.age_range.calc(age)
        # 42 CFR 435.119(b)(3) limits the adult group to people not entitled
        # to or enrolled in Medicare Part A or B. The Medicare proxy models
        # the age-65 and 24-month SSDI routes only; the immediate ALS and
        # ESRD entitlement routes are not modeled.
        medicare_eligible = person("is_medicare_eligible", period)
        # 42 CFR 435.119(b)(4) excludes people otherwise eligible for and
        # enrolled in mandatory coverage. For SSI recipients the
        # SSI-recipient category captures this: automatically in Section
        # 1634 and SSI-criteria states (42 CFR 435.120), and through the
        # state's more restrictive criteria in Section 209(b) states
        # (42 CFR 435.121).
        ssi_mandatorily_covered = person("is_ssi_recipient_for_medicaid", period)
        # Some states bar SSI receipt from the adult group outright
        # (e.g., Missouri DSS Manual § 1865.020.00, "Not receiving SSI").
        # The categorical bar excludes even an SSI recipient who fails the
        # state's more restrictive 209(b) criteria and so has no
        # mandatory-coverage pathway, closing the residual adult-group
        # route that remains open in other 209(b) states.
        state = person.household("state_code_str", period)
        excludes_all_ssi = ma.excludes_ssi_recipients[state].astype(bool)
        receives_ssi = (person("ssi", period) > 0) | (
            add(person, period, ["receives_ssi"]) > 0
        )
        ssi_excluded = ssi_mandatorily_covered | (excludes_all_ssi & receives_ssi)
        return age_eligible & ~medicare_eligible & ~ssi_excluded
