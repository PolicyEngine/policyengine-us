from policyengine_us.model_api import *


class wa_apple_health_expansion_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = (
        "Has eligible immigration status for Washington Apple Health Expansion"
    )
    definition_period = YEAR
    defined_for = StateCode.WA
    reference = [
        "https://app.leg.wa.gov/wac/default.aspx?cite=182-525-0300",
        "https://www.hca.wa.gov/about-hca/programs-and-initiatives/apple-health-medicaid/apple-health-expansion",
    ]
    documentation = """
    Washington Apple Health Expansion covers adults who are NOT eligible for
    federally funded Medicaid or QHPs with APTC due to immigration status.

    Eligible immigration statuses:
    - Undocumented immigrants

    Excluded:
    - U.S. citizens (eligible for regular Medicaid/QHPs)
    - Lawfully present immigrants (eligible for regular Medicaid/QHPs)
    - Qualified immigrants in 5-year bar (must use other programs)
    - DACA recipients: Status unclear as of January 2026. After Trump admin
      rule (effective August 25, 2025), DACA recipients lost federal ACA
      subsidies but can still use Washington Healthplanfinder with state
      Cascade Care Savings subsidies. HCA has not clarified if they are
      now eligible for Apple Health Expansion. Excluding for now.
    """

    def formula(person, period, parameters):
        immigration_status = person("immigration_status", period)

        # Only undocumented immigrants are eligible
        # They are ineligible for federal Medicaid and federal ACA subsidies
        undocumented = (
            immigration_status
            == immigration_status.possible_values.UNDOCUMENTED
        )

        # NOTE: Qualified immigrants in the federal 5-year bar (e.g., LPRs
        # who've been in the US less than 5 years) are technically excluded
        # per WAC 182-525-0300. However, we don't currently track years_in_us
        # or immigration entry date. These individuals would need to self-
        # identify their eligibility. A future enhancement could add a
        # years_in_us input variable to properly model the 5-year bar.

        # DACA recipients excluded pending HCA clarification
        # They may have access to Cascade Care Savings on state exchange

        return undocumented
