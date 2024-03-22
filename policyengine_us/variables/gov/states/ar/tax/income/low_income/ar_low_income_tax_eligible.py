from policyengine_us.model_api import *


class ar_low_income_tax_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person to utilize the Arkansas individual low income tax tables"
    definition_period = YEAR
    reference = "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2023_TaxTables.pdf"
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.ar.tax.income.rates.low_income_tax_tables
        agi = person("ar_agi", period)
        filing_status = person.tax_unit("filing_status", period)
        status = filing_status.possible_values
        dependents = person.tax_unit("tax_unit_dependents", period)
        low_income_tax = select(
            [
                filing_status == status.SINGLE,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.SEPARATE,
                filing_status == status.WIDOW,
                filing_status == status.JOINT,
            ],
            [
                p.single.calc(agi, right=True),
                where(
                    dependents <= 1,
                    p.head_of_household.no_or_one_dependent.calc(
                        agi, right=True
                    ),
                    p.head_of_household.two_or_more_dependents.calc(
                        agi, right=True
                    ),
                ),
                # Separate filers are ineligible to use the low income tax tables
                np.inf,
                where(
                    dependents <= 1,
                    p.widow.no_or_one_dependent.calc(agi, right=True),
                    p.widow.two_or_more_dependents.calc(agi, right=True),
                ),
                where(
                    dependents <= 1,
                    p.joint.no_or_one_dependent.calc(agi, right=True),
                    p.joint.two_or_more_dependents.calc(agi, right=True),
                ),
            ],
            default=0,
        )
        return low_income_tax != np.inf
