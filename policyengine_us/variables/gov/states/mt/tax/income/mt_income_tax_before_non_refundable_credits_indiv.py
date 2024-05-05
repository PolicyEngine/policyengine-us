from policyengine_us.model_api import *


class mt_income_tax_before_non_refundable_credits_indiv(Variable):
    value_type = float
    entity = Person
    label = "Montana income tax before refundable credits when married couples file separately"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        income = person("mt_taxable_income_indiv", period)
        p = parameters(period).gov.states.mt.tax.income.main
        filing_status = person.tax_unit(
            "state_filing_status_if_married_filing_separately_on_same_return",
            period,
        )
        status = filing_status.possible_values
        return select(
            [
                filing_status == status.SINGLE,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.SEPARATE,
                filing_status == status.SURVIVING_SPOUSE,
            ],
            [
                p.single.calc(income),
                p.head_of_household.calc(income),
                p.separate.calc(income),
                p.widow.calc(income),
            ],
        )
