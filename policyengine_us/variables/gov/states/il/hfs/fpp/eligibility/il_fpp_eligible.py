from policyengine_us.model_api import *


class il_fpp_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Illinois Family Planning Program eligible"
    definition_period = YEAR
    reference = (
        "https://www.dhs.state.il.us/page.aspx?item=146077",
        "https://hfs.illinois.gov/medicalclients/familyplanning.html",
        "https://www.ilga.gov/agencies/JCAR/EntirePart?titlepart=07700635",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # Note: Illinois has two Family Planning programs:
        # 1. Family Planning Presumptive Eligibility (FPPE) - temporary
        #    coverage, does NOT require citizenship/immigration status
        # 2. Ongoing Family Planning Program - 1 year coverage, REQUIRES
        #    US citizenship or qualified immigrant status
        # This variable models the ongoing program. The only eligibility
        # difference between the two is the immigration requirement.

        income_eligible = person("il_fpp_income_eligible", period)
        # Must NOT be pregnant (pregnant individuals should apply for
        # maternal health programs instead)
        not_pregnant = ~person("is_pregnant", period)
        # Use shared IL HFS immigration status check
        immigration_eligible = person(
            "il_hfs_immigration_status_eligible", period
        )
        # Cannot be enrolled in other non-spenddown full medical coverage
        not_on_medicaid = ~person("receives_medicaid", period)
        return (
            income_eligible
            & not_pregnant
            & immigration_eligible
            & not_on_medicaid
        )
