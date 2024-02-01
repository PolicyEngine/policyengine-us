from policyengine_us.model_api import *


class ar_low_income_tax_indiv(Variable):
    value_type = float
    entity = Person
    label = (
        "Arkansas low income tax when married couples are filing separately"
    )
    unit = USD
    definition_period = YEAR
    reference = "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=29"
    defined_for = "ar_can_file_separate_on_same_return"

    def formula(person, period, parameters):
        agi = person("ar_agi", period)
        p = parameters(
            period
        ).gov.states.ar.tax.income.rates.low_income_tax_tables
        filing_status_separate = person.tax_unit(
            "state_filing_status_if_married_filing_separately_on_same_return",
            period,
        )
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
                (filing_status_separate == status.WIDOW) & (dependents <= 1),
                (filing_status_separate == status.WIDOW) & (dependents > 1),
            ],
            [
                p.single.calc(agi, right=True),
                p.head_of_household.no_or_one_dependent.calc(agi, right=True),
                p.head_of_household.two_or_more_dependents.calc(
                    agi, right=True
                ),
                p.separate.calc(agi, right=True),
                p.widow.no_or_one_dependent.calc(agi, right=True),
                p.widow.two_or_more_dependents.calc(agi, right=True),
            ],
            default=0,
        )
