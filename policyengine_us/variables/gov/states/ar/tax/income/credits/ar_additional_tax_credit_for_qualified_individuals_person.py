from policyengine_us.model_api import *


class ar_additional_tax_credit_for_qualified_individuals_person(Variable):
    value_type = float
    entity = Person
    label = "Arkansas additional tax credit for qualified individuals for each individual"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        filing_separately = person.tax_unit("ar_files_separately", period)
        income_joint = person("ar_taxable_income_joint", period)
        income_indiv = person("ar_taxable_income_indiv", period)
        # When filing separately, the credit is calculated based on individual income
        income = where(
            filing_separately, income_indiv, person.tax_unit.sum(income_joint)
        )
        p = parameters(
            period
        ).gov.states.ar.tax.income.credits.additional_tax_credit_for_qualified_individuals
        filing_status = person.tax_unit("filing_status", period)
        joint = filing_status == filing_status.possible_values.JOINT
        filing_jointly = joint & ~filing_separately
        multiplier = where(filing_jointly, p.joint_multiplier, 1)
        max_amount = where(
            filing_jointly, p.max_amount * multiplier, p.max_amount
        )
        excess = max_(income - p.reduction.start, 0)
        increments = np.ceil(excess / p.reduction.increment)
        reduction_amount = where(
            filing_jointly,
            p.reduction.amount * multiplier,
            p.reduction.amount,
        )
        total_reduction_amount = increments * reduction_amount
        # Attribute the maximum amount to each spouse equally when married filing jointly
        divisor = where(filing_jointly, 2, 1)
        total_credit = max_(max_amount - total_reduction_amount, 0) / divisor
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return total_credit * head_or_spouse
