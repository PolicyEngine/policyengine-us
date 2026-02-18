from policyengine_us.model_api import *


class ar_files_separately(Variable):
    value_type = bool
    entity = TaxUnit
    label = "married couple files separately on the Arkansas tax return"
    definition_period = YEAR
    reference = (
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2023_AR1000F_and_AR1000NR_Instructions.pdf",
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2023_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf",
    )
    defined_for = StateCode.AR

    def formula(tax_unit, period, parameters):
        itax_indiv = add(
            tax_unit,
            period,
            ["ar_income_tax_before_non_refundable_credits_indiv"],
        )
        itax_joint = add(
            tax_unit,
            period,
            ["ar_income_tax_before_non_refundable_credits_joint"],
        )
        # The additional tax credit for qualified individuals uses
        # different income bases for joint vs separate filing,
        # which can change which path is cheaper. Other credits
        # (personal, CDCC) are the same for both paths. We compute
        # the credit for each path independently to avoid a circular
        # dependency (ar_files_separately -> credit -> ar_files_separately).
        # KEEP IN SYNC with
        # ar_additional_tax_credit_for_qualified_individuals_person.py
        p = parameters(
            period
        ).gov.states.ar.tax.income.credits.additional_tax_credit_for_qualified_individuals
        person = tax_unit.members
        filing_status = tax_unit("filing_status", period)
        joint = filing_status == filing_status.possible_values.JOINT
        # Joint path credit: uses net taxable income (AGI when low
        # income table applies) with joint multiplier.
        net_income = person("ar_net_taxable_income_joint", period)
        joint_income = tax_unit.sum(net_income)
        multiplier = where(joint, p.joint_multiplier, 1)
        max_joint = p.max_amount * multiplier
        increment = max_(p.reduction.increment, 1)
        excess_joint = max_(joint_income - p.reduction.start, 0)
        increments_joint = np.ceil(excess_joint / increment)
        reduction_joint = increments_joint * p.reduction.amount * multiplier
        credit_joint = max_(max_joint - reduction_joint, 0)
        # Separate path credit: uses individual taxable income.
        indiv_income = person("ar_taxable_income_indiv", period)
        excess_sep = max_(indiv_income - p.reduction.start, 0)
        increments_sep = np.ceil(excess_sep / increment)
        reduction_sep = increments_sep * p.reduction.amount
        sep_credit_person = max_(p.max_amount - reduction_sep, 0)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        credit_sep = tax_unit.sum(sep_credit_person * head_or_spouse)
        # Compare after filing-method-sensitive credits.
        return (itax_indiv - credit_sep) < (itax_joint - credit_joint)
