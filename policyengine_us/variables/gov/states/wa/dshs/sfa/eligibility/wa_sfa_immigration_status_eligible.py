from policyengine_us.model_api import *


class wa_sfa_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Washington State Family Assistance immigration status eligible"
    definition_period = MONTH
    defined_for = StateCode.WA
    reference = (
        # WAC 388-400-0010(2)(a): qualified-alien-in-5-year-bar SFA pathway.
        "https://app.leg.wa.gov/wac/default.aspx?cite=388-400-0010",
        "https://app.leg.wa.gov/wac/default.aspx?cite=388-424-0015",
    )
    # The qualified-alien-in-5-year-bar pathway (WAC 388-424-0015(1)(a)) is
    # modeled here. The 19-20 year old student pathway (WAC 388-400-0010(2)(c))
    # and the caretaker-relative pathway (2)(d) are modeled separately via
    # wa_sfa_student_pathway_eligible. Other SFA pathways from
    # WAC 388-400-0010 — nonqualified aliens meeting WA residency,
    # T/U-visa and VAWA survivors of certain crimes, and pregnant women
    # convicted of multi-state fraud — are not tracked at the moment.

    def formula(person, period, parameters):
        is_qualified = person("is_citizen_or_legal_immigrant", period.this_year)
        tanf_immigration_eligible = person(
            "wa_tanf_immigration_status_eligible", period
        )
        return is_qualified & ~tanf_immigration_eligible
