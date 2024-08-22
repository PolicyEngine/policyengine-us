from policyengine_us.model_api import *


class ar_inflation_relief_credit_person(Variable):
    value_type = float
    entity = Person
    label = "Arkansas inflation relief income-tax credit for each individual"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        # the Arkansas inflationary relief tax credit is calculated based on net taxable income
        # mentioned in individual income tax return form AR1000F line 28
        filing_separately = person.tax_unit("ar_files_separately", period)
        income_joint = person("ar_taxable_income_joint", period)
        income_indiv = person("ar_taxable_income_indiv", period)
        # When filing separartely, the credit is calculated based on individual income
        income = where(
            filing_separately, income_indiv, person.tax_unit.sum(income_joint)
        )
        p = parameters(
            period
        ).gov.states.ar.tax.income.credits.inflationary_relief
        filing_status = person.tax_unit("filing_status", period)
        max_amount = p.max_amount[filing_status]
        reduction_start = p.reduction.start[filing_status]
        increment = p.reduction.increment[filing_status]
        reduction_per_increment = p.reduction.amount[filing_status]
        excess = max_(income - reduction_start, 0)
        increments = np.ceil(excess / increment)
        total_reduction_amount = increments * reduction_per_increment
        return max_(max_amount - total_reduction_amount, 0)
