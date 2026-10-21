from policyengine_us.model_api import *


class ia_ssa_nonfinancial_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Iowa SSA nonfinancial eligibility"
    definition_period = MONTH
    defined_for = StateCode.IA
    reference = (
        # Iowa Code 249.3
        "https://www.legis.iowa.gov/docs/code/249.pdf#page=2",
        # 441 IAC 51.2 and 51.7(2); PDF pages 1-2
        "https://www.legis.iowa.gov/docs/iac/chapter/441.51.pdf#page=1",
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
        # NOTE: Iowa Code 249.3(4)(a) limits the SMME supplement to a person
        # "Sixty-five years of age or older" or "Disabled as defined by 42
        # U.S.C. §1382c(a)(3)". 441 IAC 51.7(2) requires "all eligibility
        # requirements for supplemental security income benefits other than
        # limits on substantial gainful activity and income", and 6-B p.76
        # starts from "the SSI eligibility requirements", which include
        # blindness (p.10). Where a statute and a rule or manual disagree, the
        # model follows the statute (the statute-first rule in CONTRIBUTING.md), so a
        # blind person under 65 who is not disabled gets no SMME, while one who
        # is disabled does (ia_ssa.yaml Cases 72 and 76).
        aged_blind_disabled = person("is_ssi_aged_blind_disabled", period.this_year)
        aged_or_disabled = person("is_ssi_aged", period.this_year) | person(
            "is_ssi_disabled", period.this_year
        )
        smme = category == category.possible_values.SMME
        return (
            where(smme, aged_or_disabled, aged_blind_disabled)
            & (citizen | immigrant)
            & (category != category.possible_values.NONE)
            & ~person("is_incarcerated", period)
            & pursues_ssi
        )
