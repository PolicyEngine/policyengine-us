from policyengine_us.model_api import *


class ar_low_income_tax_joint(Variable):
    value_type = float
    entity = Person
    label = (
        "Arkansas low income tax when married couples are filing separately"
    )
    unit = USD
    definition_period = YEAR
    reference = "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=29"
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        agi = add(person.tax_unit, period, ["ar_agi_joint"])
        head = person("is_tax_unit_head", period)
        agi_attributed_to_head = agi * head
        p = parameters(
            period
        ).gov.states.ar.tax.income.rates.low_income_tax_tables
        filing_status_separate = person.tax_unit("filing_status", period)
        status = filing_status_separate.possible_values
        dependents = person.tax_unit("tax_unit_dependents", period)
        return select(
            [
                filing_status_separate == status.SINGLE,
                (filing_status_separate == status.HEAD_OF_HOUSEHOLD)
                & (dependents <= 1),
                (filing_status_separate == status.HEAD_OF_HOUSEHOLD)
                & (dependents > 1),
                filing_status_separate == status.SEPARATE,
                (filing_status_separate == status.SURVIVING_SPOUSE)
                & (dependents <= 1),
                (filing_status_separate == status.SURVIVING_SPOUSE)
                & (dependents > 1),
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
                p.joint.no_or_one_dependent.calc(
                    agi_attributed_to_head, right=True
                ),
                p.joint.two_or_more_dependents.calc(
                    agi_attributed_to_head, right=True
                ),
            ],
            default=0,
        )
