from policyengine_us.model_api import *


class mt_capital_gains_tax_applicable_threshold_joint(Variable):
    value_type = float
    entity = Person
    label = "Montana applicable threshold for the capital gains tax when married couples file jointly"
    unit = USD
    definition_period = YEAR
    reference = "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/12/Form_2_2023_Instructions.pdf#page=6"  # Net Long-Term Capital Gains Tax Table
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.main.capital_gains
        capital_gains = person("long_term_capital_gains", period)
        taxable_income = person("mt_taxable_income_indiv", period)
        filing_status = person.tax_unit(
            "filing_status",
            period,
        )
        status = filing_status.possible_values
        non_qualified_income = max_(taxable_income - capital_gains, 0)
        rate_threshold = select(
            [
                filing_status == status.SINGLE,
                filing_status == status.SEPARATE,
                filing_status == status.JOINT,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.SURVIVING_SPOUSE,
            ],
            [
                p.rates.single.thresholds[-1],
                p.rates.separate.thresholds[-1],
                p.rates.joint.thresholds[-1],
                p.rates.head_of_household.thresholds[-1],
                p.rates.surviving_spouse.thresholds[-1],
            ],
        )
        return max_(rate_threshold - non_qualified_income, 0)
