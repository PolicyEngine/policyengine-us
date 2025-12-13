from policyengine_us.model_api import *


class il_aabd_non_financial_eligible_person(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Eligible person for Illinois Aid to the Aged, Blind or Disabled (AABD)"
    reference = (
        "https://www.law.cornell.edu/regulations/illinois/title-89/part-113/subpart-B",
        "https://www.dhs.state.il.us/page.aspx?item=15910",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # Per IDHS Policy Manual PM 11-01-00, a person must either:
        # 1. Receive SSI, OR
        # 2. Be ineligible for SSI due to income (but meet all other SSI requirements)
        #
        # Note: The policy manual only mentions "disabled" for under-65 persons
        # who are SSI-ineligible due to income, but 89 Ill. Admin. Code 113.40(b)
        # explicitly states: "The Department will make the determination of
        # blindness when the client has been denied SSI on the basis of too
        # much income." So blind persons are also covered.
        #
        # is_ssi_eligible checks categorical (aged/blind/disabled), resources,
        # and immigration status for SSI. If True, person qualifies for IL AABD
        # regardless of whether they actually receive SSI (income may be too high).
        ssi_status_eligible = person("is_ssi_eligible", period.this_year)

        # IL AABD has additional qualified noncitizen categories beyond SSI
        # (e.g., abuse victims, trafficking victims, military families per
        # 89 Ill. Admin. Code 113.10), so we check IL-specific immigration.
        immigration_status_eligible = person(
            "il_aabd_immigration_status_eligible_person", period
        )

        return ssi_status_eligible & immigration_status_eligible
