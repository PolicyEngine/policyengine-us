from policyengine_us.model_api import *


class head_start_qualifying_months(Variable):
    value_type = int
    entity = Person
    label = "Months of the year Head Start eligibility covers"
    unit = "month"
    definition_period = YEAR
    documentation = (
        "Months of the year that Head Start and Early Head Start eligibility "
        "covers: twelve, unless the family qualifies only through public "
        "assistance that the model measures by month (SNAP, SSI, or reported "
        "SNAP, TANF or SSI receipt) and that assistance starts after January. "
        "Then it counts the months from the first month of assistance through "
        "December. Once a program determines a child eligible, the child "
        "keeps that eligibility through the end of the succeeding program "
        "year, or while participating in Early Head Start, so later months "
        "count even if the assistance stops. The model holds no earlier "
        "years, so it treats the first "
        "month of assistance in the year as the family's first. Income, "
        "homelessness, foster care and TANF, which the model computes by "
        "year, cover the whole year."
    )
    reference = (
        "https://www.ecfr.gov/current/title-45/section-1302.12#p-1302.12(j)",
        # ACF IM 22-03 interprets SNAP as qualifying public assistance
        # under 45 CFR 1302.12(c)(1)(ii).
        "https://www.headstart.gov/policy/im/acf-im-hs-22-03",
    )

    def formula(person, period, parameters):
        # The model measures these tests by year, so each covers the year.
        whole_year = (
            person("is_head_start_income_eligible", period)
            | person.household("is_homeless", period)
            | person("was_in_foster_care", period)
            | (person.spm_unit("tanf", period) > 0)
        )
        # Count the months from the first month of public assistance that
        # the model measures by month. Eligibility continues after that
        # month (45 CFR 1302.12(j)), so a month counts once any earlier
        # month in the year had assistance.
        assisted_yet = False
        months_from_first_assistance = 0
        for month in period.get_subperiods(MONTH):
            assisted = (add(person.spm_unit, month, ["snap", "ssi"]) > 0) | (
                add(
                    person.spm_unit,
                    month,
                    ["receives_snap", "receives_tanf", "receives_ssi"],
                )
                > 0
            )
            assisted_yet = assisted_yet | assisted
            months_from_first_assistance = months_from_first_assistance + assisted_yet
        starts_after_january = (
            ~whole_year
            & (months_from_first_assistance > 0)
            & (months_from_first_assistance < MONTHS_IN_YEAR)
        )
        return where(starts_after_january, months_from_first_assistance, MONTHS_IN_YEAR)
