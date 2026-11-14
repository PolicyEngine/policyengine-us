from policyengine_us.model_api import *


class medicaid_federal_share(Variable):
    value_type = float
    entity = Person
    label = "Medicaid federal share (FMAP applicable to enrollee)"
    documentation = (
        "Federal medical assistance percentage applied to this enrollee's "
        "Medicaid expenditures. Uses the ACA expansion FMAP for expansion "
        "adults (42 U.S.C. 1396d(y)) and the state's regular FMAP for all "
        "other enrollment groups (42 U.S.C. 1396d(b)). Title XIX pays only "
        "for an enrollee in a Medicaid group who meets the federal "
        "immigration test, which includes the lawfully residing option for "
        "children and pregnant people (42 U.S.C. 1396b(v)(1) and (4)). Every "
        "other enrollee reaches Medicaid only through state-funded coverage "
        "and gets no federal share. That coverage includes state coverage "
        "regardless of immigration status (California's state-funded "
        "Medi-Cal, former foster youth coverage included, and states that "
        "cover undocumented immigrants) and Illinois Health Benefits for "
        "Immigrants. It also includes Rhode Island's postpartum continuation "
        "outside the pregnancy group: RIte Start serves people not eligible "
        "under Title XIX or XXI, and CHIP and FCEP pregnancies are Title XXI "
        "coverage. An enrollee who also meets a federally matched group keeps "
        "that group's match. Title XIX matches emergency services for "
        "enrollees who fail the immigration test (42 U.S.C. 1396b(v)(2)), but "
        "per-enrollee cost is not split by service, so that match is not "
        "included. Separate Title XXI health services initiative funding is "
        "not included either."
    )
    unit = "/1"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396d",
        "https://www.law.cornell.edu/uscode/text/42/1396b#v",
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=14007.8.&lawCode=WIC",
        "https://www.ilga.gov/Documents/legislation/ilcs/documents/030500050K12-4.35.htm",
        "https://webserver.rilegislature.gov/Statutes/TITLE42/42-12.3/42-12.3-3.htm",
        "https://www.medicaid.gov/medicaid/spa/downloads/RI-22-0024.pdf#page=7",
        "https://www.medicaid.gov/CHIP/Downloads/RI-22-0026.pdf#page=2",
    )
    defined_for = "medicaid_enrolled"

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicaid.cost_share
        state = person.household("state_code", period)
        regular_fmap = p.fmap[state]
        category = person("medicaid_category", period)
        categories = category.possible_values
        # 42 U.S.C. 1396b(v)(1) bars Title XIX payment for an enrollee who
        # fails the federal immigration test, apart from emergency services.
        # is_medicaid_immigration_status_eligible also counts state-funded
        # coverage, so the federal test is used here.
        federally_matched_route = (category != categories.NONE) & person(
            "is_federal_medicaid_immigration_status_eligible", period
        )
        no_federal_medicaid_match = ~federally_matched_route
        return select(
            [
                no_federal_medicaid_match,
                category == categories.ADULT,
                category != categories.NONE,
            ],
            [0, p.expansion_fmap, regular_fmap],
            default=0,
        )
