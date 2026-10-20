from policyengine_us.model_api import *


class ia_ssa_nonfinancial_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Iowa SSA nonfinancial eligibility"
    definition_period = MONTH
    defined_for = StateCode.IA
    reference = (
        # Iowa Code 249.3
        "https://www.legis.iowa.gov/docs/code/249.pdf#page=1",
        # PDF pages 6, 8, 10-12
        "https://hhs.iowa.gov/media/3987/download?inline=#page=6",
    )

    def formula(person, period, parameters):
        category = person("ia_ssa_category", period)
        immigration = person("immigration_status", period.this_year)
        citizen = immigration == immigration.possible_values.CITIZEN
        immigrant = person("is_ssi_qualified_noncitizen", period.this_year)
        # 6-B Nonfinancial Eligibility: applicants "must also apply for SSI or
        # FIP if they might be eligible". An applicant whose income would
        # qualify for SSI must take it up; one over income for SSI need not.
        pursues_ssi = person("takes_up_ssi_if_eligible", period.this_year) | (
            person("uncapped_ssi", period) <= 0
        )
        # NOTE: The SMME exception for a disabled person engaged in substantial
        # gainful activity (Iowa Code 249.3(4)(a)(2); 441 IAC 51.7(2); 6-B p.10:
        # "an applicant must meet disability standards other than the inability
        # to engage in substantial gainful activity") is not modeled, because
        # is_ssi_disabled excludes people working above the SGA level.
        return (
            person("is_ssi_aged_blind_disabled", period.this_year)
            & (citizen | immigrant)
            & (category != category.possible_values.NONE)
            & ~person("is_incarcerated", period)
            & pursues_ssi
        )
