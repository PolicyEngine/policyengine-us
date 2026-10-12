from policyengine_us.model_api import *


class ca_wdp_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = "California 250 Percent Working Disabled Program income eligible"
    definition_period = YEAR
    documentation = (
        "Whether this person passes the California 250% Working Disabled "
        "Program net family income test. This first-pass model uses the "
        "applicant's income plus spouse income only when SSI spousal deeming "
        "applies, and caps the FPL unit at the applicant plus spouse. Parent "
        "deeming for child applicants is not modeled."
    )
    reference = "https://www.dhcs.ca.gov/services/working-disabled-program/"
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ca.chhs.wdp.eligibility.income
        personal_income = person("ca_wdp_countable_income", period)
        spouse_income = person.marital_unit.sum(personal_income) - personal_income
        spousal_deeming_applies = person("is_ssi_spousal_deeming_applies", period)
        countable_income = personal_income + where(
            spousal_deeming_applies,
            spouse_income,
            0,
        )

        fpg = parameters(period).gov.hhs.fpg
        state_group = person.household("state_group_str", period)
        unit_size = where(spousal_deeming_applies, 2, 1)
        fpg_amount = (
            fpg.first_person[state_group]
            + (unit_size - 1) * fpg.additional_person[state_group]
        )
        income_limit = fpg_amount * p.limit
        return countable_income < income_limit
