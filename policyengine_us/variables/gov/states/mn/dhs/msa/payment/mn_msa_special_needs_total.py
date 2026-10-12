from policyengine_us.model_api import *


class mn_msa_special_needs_total(Variable):
    value_type = float
    entity = Person
    label = "Minnesota Supplemental Aid total special-needs allowance"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256D.44",
        "https://www.dhs.state.mn.us/main/groups/county_access/documents/pub/mndhs-073585.pdf#page=4",
    )

    def formula(person, period, parameters):
        # Guardian fee and housing allowance are not paid in Medicaid
        # facilities; representative payee fee is paid in all settings.
        arrangement = person("mn_msa_payment_category", period)
        in_facility = arrangement == arrangement.possible_values.MEDICAID_FACILITY
        representative_payee = person("mn_msa_representative_payee_fee", period)
        community_special_needs = add(
            person,
            period,
            ["mn_msa_guardian_fee", "mn_msa_housing_assistance"],
        )
        return representative_payee + where(in_facility, 0, community_special_needs)
