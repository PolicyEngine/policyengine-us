from policyengine_us.model_api import *


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
        # initial month"; spouses who both enter in the same month are taken
        # to share a room (ia_ssa.yaml Cases 57, 59 and 60). A resident with an
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
        couple = person("ssi_couple_computation_applies", period) & person(
            "ia_ssa_has_spouse", period
        )
        receives_ssi = (person("ssi", period) > 0) | person("receives_ssi", period)
        couple_received_ssi = person.marital_unit.any(receives_ssi)
        both_enter = person.marital_unit.sum(entering) == 2
        return entering & couple & (couple_received_ssi | both_enter)
