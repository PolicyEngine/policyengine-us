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
        # When using the low income tax table, the standard deduction is
        # built in, so net taxable income equals AGI. Otherwise it equals
        # AGI minus deductions (the regular taxable income).
        net_income_joint = person("ar_net_taxable_income_joint", period)
        joint_income = person.tax_unit.sum(net_income_joint)
        indiv_income = person("ar_taxable_income_indiv", period)
        income = where(filing_separately, indiv_income, joint_income)
        p = parameters(period).gov.states.ar.tax.income.credits.inflationary_relief
        filing_status = person.tax_unit("filing_status", period)
        statuses = filing_status.possible_values
        # A married couple filing combined (status 4) computes the credit for
        # each spouse separately in the single-filer table (max $150, phased
        # out from $87,000), per the Inflationary Relief Credit Worksheet.
        # Only a true joint return (status 2) uses the joint table (max $300,
        # phased out from $174,000) on combined income and splits it in half.
        credit_status = statuses.encode(
            where(filing_separately, statuses.SEPARATE, filing_status.decode())
        )
        max_amount = p.max_amount[credit_status]
        reduction_start = p.reduction.start[credit_status]
        increment = p.reduction.increment[credit_status]
        reduction_per_increment = p.reduction.amount[credit_status]
        excess = max_(income - reduction_start, 0)
        increments = np.ceil(excess / increment)
        total_reduction_amount = increments * reduction_per_increment
        # Attribute the maximum amount to each spouse equally only when the
        # couple files a true joint return (combined filers already use their
        # own individual income above).
        true_joint = (filing_status == statuses.JOINT) & ~filing_separately
        divisor = where(true_joint, 2, 1)
        credit = max_(max_amount - total_reduction_amount, 0) / divisor
        # The credit is only allocated to the head and spouse, not dependents.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return credit * head_or_spouse
