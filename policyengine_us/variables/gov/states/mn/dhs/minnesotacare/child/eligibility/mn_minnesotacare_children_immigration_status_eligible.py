from policyengine_us.model_api import *


class mn_minnesotacare_children_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Has eligible immigration status for MinnesotaCare for children"
    definition_period = YEAR
    defined_for = StateCode.MN
    reference = [
        "https://www.revisor.mn.gov/statutes/cite/256L.04",
        "https://www.dhs.state.mn.us/main/groups/publications/documents/pub/mndhs-068276.pdf",
    ]
    documentation = """
    MinnesotaCare for undocumented children covers those who are ineligible
    for federal medical assistance by reason of immigration status.

    Per Minnesota Statutes 256L.04 subdivision 10:
    "Notwithstanding subdivisions 1 and 7, eligible persons include families
    and individuals who are ineligible for medical assistance by reason of
    immigration status and who have incomes equal to or less than 200 percent
    of federal poverty guidelines."

    This state-funded coverage is for undocumented children who cannot access
    federal Medicaid or CHIP due to their immigration status. Coverage is
    delivered on a fee-for-service basis.
    """

    def formula(person, period, parameters):
        immigration_status = person("immigration_status", period)

        # Only undocumented immigrants are eligible for this state-funded program
        # Citizens and lawfully present immigrants should access federal programs
        undocumented = (
            immigration_status
            == immigration_status.possible_values.UNDOCUMENTED
        )

        return undocumented
