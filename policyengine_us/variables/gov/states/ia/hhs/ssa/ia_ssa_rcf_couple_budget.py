from policyengine_us.model_api import *
from policyengine_us.variables.gov.states._spouses import (
    state_couple_total,
    state_is_married,
)
from policyengine_us.variables.gov.states.ia.hhs.ssa._ia_ssa_spouses import (
    ia_ssa_spouse_value,
)


class ia_ssa_rcf_couple_budget(Variable):
    value_type = bool
    entity = Person
    label = "Iowa SSA residential care couple budget in the month of entry"
    definition_period = MONTH
    defined_for = StateCode.IA
    reference = (
        # 441 IAC 51.4(3); PDF pages 1-2
        "https://www.legis.iowa.gov/docs/iac/chapter/441.51.pdf#page=1",
        # PDF pages 60-61, 67-71
        "https://hhs.iowa.gov/media/3987/download?inline=#page=60",
    )

    def formula(person, period, parameters):
        # 6-B Spouses Living Separately p.60: "When one or both spouses are
        # receiving SSI before one or both enters an RCF, treat the spouses as
        # a couple during the month of entry, then as individuals beginning the
        # month after the month of entry", and "When neither spouse is
        # receiving SSI before the entry of one or both into an RCF, treat the
        # spouses separately beginning in the month of entry." 441 IAC 51.4(3)
        # makes "Partners in a marriage who both enter the same room of the
        # residential care facility in the same month" a couple for "the
        # initial month"; sharing a room is an explicit input. A resident with an
        # ineligible spouse is budgeted alone (ia_ssa.yaml Case 73); SSI's
        # first-month deemed income from that spouse (6-B p.60) is not modeled.
        # NOTE: A spouse who enters after the other spouse's month of entry
        # also gets the couple budget when either spouse received SSI, while
        # the spouse already in the facility stays on the individual budget. 51.4(3) covers spouses who "both
        # enter" in the same month, and p.61 makes a couple of spouses sharing
        # a room "During their first month in the RCF", so neither settles a
        # later entry.
        category = person("ia_ssa_category", period)
        rcf = category == category.possible_values.RESIDENTIAL_CARE
        entering = rcf & person("ia_ssa_care_initial_partial_month", period)
        year = period.this_year
        # The prior-SSI entry-month rule retains the declared marriage even
        # when the spouses have moved to separate facilities. Ordinary Iowa
        # spouse pooling still requires co-residence (ia_ssa_has_spouse).
        couple = state_is_married(person, year) & (
            state_couple_total(
                person, year, person("is_ssi_aged_blind_disabled", year).astype(int)
            )
            == 2
        )
        # Keep the existing SSI computation guard for spouses still living
        # together. The state entry exception supplies only the spouse link
        # federal SSI drops when the spouses occupy separate households. A
        # rejected co-resident pair (such as a parent and adult child in the
        # default marital unit) does not establish that the people live apart.
        household = person.household.reference_entity.members_entity_id
        apart = state_couple_total(person, year, household) != 2 * household
        couple = couple & (apart | person("ssi_couple_computation_applies", period))
        receives_ssi = (person("ssi", period) > 0) | person("receives_ssi", period)
        # Separated spouses need an explicit pre-entry receipt fact. For
        # co-resident legacy situations, current receipt still approximates
        # pre-entry receipt; a newly awarded current-month payment cannot
        # establish prior receipt for spouses now in separate households.
        receives_ssi = person("ia_ssa_rcf_received_ssi_before_entry", period) | (
            person("ia_ssa_has_spouse", period) & receives_ssi
        )
        couple_received_ssi = (
            state_couple_total(person, year, receives_ssi.astype(int)) > 0
        )
        both_enter = state_couple_total(person, year, entering.astype(int)) == 2
        room = person("ia_ssa_rcf_shares_room_with_spouse", period)
        same_room = person("ia_ssa_has_spouse", period) & (
            room | ia_ssa_spouse_value(person, period, room)
        )
        return entering & couple & (couple_received_ssi | (both_enter & same_room))
