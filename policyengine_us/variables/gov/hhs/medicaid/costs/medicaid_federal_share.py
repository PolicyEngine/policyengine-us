from policyengine_us.model_api import *


class medicaid_federal_share(Variable):
    value_type = float
    entity = Person
    label = "Medicaid federal share (FMAP applicable to enrollee)"
    documentation = (
        "Federal medical assistance percentage applied to this enrollee's "
        "Medicaid expenditures. Uses the ACA expansion FMAP for expansion "
        "adults (42 U.S.C. 1396d(y)) and the state's regular FMAP for all "
        "other enrollment groups (42 U.S.C. 1396d(b)). Rhode Island's "
        "postpartum continuation receives no Title XIX match unless the "
        "pregnancy was covered by Medicaid and the enrollee meets Medicaid "
        "immigration requirements: RIte Start serves people not eligible "
        "under Title XIX or XXI, and CHIP and FCEP pregnancies are Title XXI "
        "coverage. The zero match applies even if the enrollee also meets "
        "another federally matched group. Separate Title XXI health services "
        "initiative funding is not included here."
    )
    unit = "/1"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396d",
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
        pregnancy_coverage = person("ri_pregnancy_coverage", period)
        coverage_types = pregnancy_coverage.possible_values
        federally_matched_pregnancy = (
            pregnancy_coverage == coverage_types.MEDICAID
        ) & person("is_medicaid_immigration_status_eligible", period)
        no_federal_medicaid_match = (
            (state == StateCode.RI)
            & person("ri_medicaid_postpartum_eligible", period.first_month)
            & ~federally_matched_pregnancy
        )
        return select(
            [
                no_federal_medicaid_match,
                category == categories.ADULT,
                category != categories.NONE,
            ],
            [0, p.expansion_fmap, regular_fmap],
            default=0,
        )
