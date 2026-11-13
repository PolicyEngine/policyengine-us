from policyengine_us.model_api import *


class ar_low_income_tax_joint(Variable):
    value_type = float
    entity = Person
    label = "Arkansas low income tax when married couples are filing separately"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dfa.arkansas.gov/wp-content/uploads/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=29",
        "https://www.arkleg.state.ar.us/Home/FTPDocument?path=/ACTS/2021R/Public/ACT483.pdf#page=3",
        "https://www.dfa.arkansas.gov/wp-content/uploads/2025_AR1000F_and_AR1000NR_Instructions.pdf#page=12",
        "https://www.dfa.arkansas.gov/wp-content/uploads/TaxTables_FI_2025.pdf#page=3",
    )
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        # A spouse's loss can make the joint total negative; the tax base
        # cannot be.
        agi = max_(add(person.tax_unit, period, ["ar_agi_joint"]), 0)
        head = person("is_tax_unit_head", period)
        agi_attributed_to_head = agi * head
        p = parameters(period).gov.states.ar.tax.income.rates.low_income_tax_tables
        filing_status_separate = person.tax_unit("filing_status", period)
        status = filing_status_separate.possible_values
        # Arkansas leaves the table's dependent count undefined in 26-51-301.
        # We use the form's line 7B count to fill that gap: IRC 152 dependents
        # under 26-51-501(a)(3)(B), not unrestricted household members.
        # IRC 152(b)(1) leaves none when either filer can be claimed.
        # The would-be claimant's filing exception (not required to file and
        # filing only for a refund, Publication 501) restores the dependents.
        filer_is_dependent = person.tax_unit(
            "head_or_spouse_is_dependent_elsewhere_without_filing_exception", period
        )
        dependents = where(
            filer_is_dependent, 0, person.tax_unit("tax_unit_dependents", period)
        )
        return select(
            [
                filing_status_separate == status.SINGLE,
                (filing_status_separate == status.HEAD_OF_HOUSEHOLD)
                & (dependents <= 1),
                (filing_status_separate == status.HEAD_OF_HOUSEHOLD) & (dependents > 1),
                filing_status_separate == status.SEPARATE,
                (filing_status_separate == status.SURVIVING_SPOUSE) & (dependents <= 1),
                (filing_status_separate == status.SURVIVING_SPOUSE) & (dependents > 1),
                (filing_status_separate == status.JOINT) & (dependents <= 1),
                (filing_status_separate == status.JOINT) & (dependents > 1),
            ],
            [
                p.single.calc(agi_attributed_to_head, right=True),
                p.head_of_household.no_or_one_dependent.calc(
                    agi_attributed_to_head, right=True
                ),
                p.head_of_household.two_or_more_dependents.calc(
                    agi_attributed_to_head, right=True
                ),
                # Separate filers are ineligible to use the low income tax tables
                np.inf,
                p.surviving_spouse.no_or_one_dependent.calc(
                    agi_attributed_to_head, right=True
                ),
                p.surviving_spouse.two_or_more_dependents.calc(
                    agi_attributed_to_head, right=True
                ),
                p.joint.no_or_one_dependent.calc(agi_attributed_to_head, right=True),
                p.joint.two_or_more_dependents.calc(agi_attributed_to_head, right=True),
            ],
            default=0,
        )
