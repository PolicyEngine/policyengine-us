from policyengine_us.model_api import *


class nd_mpc(Variable):
    value_type = float
    entity = TaxUnit
    label = "ND marriage-penalty nonrefundable credit amount"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.tax.nd.gov/sites/www/files/documents/forms/form-nd-1-2021.pdf"
        "https://www.tax.nd.gov/sites/www/files/documents/forms/2021-individual-income-tax-booklet.pdf"
        "https://www.tax.nd.gov/sites/www/files/documents/forms/form-nd-1-2022.pdf"
        "https://www.tax.nd.gov/sites/www/files/documents/forms/2022-individual-income-tax-booklet.pdf"
    )
    defined_for = StateCode.ND

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nd.tax.income.credits
        # determine credit eligibility
        # ... joint filing status?
        filing_status = tax_unit("filing_status", period)
        joint = filing_status == filing_status.possible_values.JOINT
        # ... high taxable income?
        taxinc = tax_unit("nd_taxable_income", period)
        hi_taxinc = taxinc > p.marriage_penalty.taxable_income_threshold
        eligible = joint & hi_taxinc
        # determine minimum qualified income between head and spouse
        qinc_sources = [
            "employment_income",
            "self_employment_income",
            "taxable_pension_income",
        ]
        person = tax_unit.members
        setax_ded = person("self_employment_tax_ald_person", period)
        qinc_person = add(person, period, qinc_sources) - setax_ded
        is_head = person("is_tax_unit_head", period)
        qinc_head = tax_unit.sum(qinc_person * is_head)
        is_spouse = person("is_tax_unit_spouse", period)
        qinc_spouse = tax_unit.sum(qinc_person * is_spouse)
        min_qinc = min_(qinc_head, qinc_spouse)
        hi_min_qinc = min_qinc > p.marriage_penalty.qualified_income_threshold
        # calculate uncapped credit amount
        tax = parameters(period).gov.states.nd.tax.income.rates
        tinc1 = max_(0, min_qinc - p.marriage_penalty.taxable_income_base)
        taxs1 = tax.single.calc(tinc1)
        tinc2 = max_(0, taxinc - tinc1)
        taxs2 = tax.single.calc(tinc2)
        taxj = tax_unit("nd_income_tax_before_credits", period)
        mpc_amount = max_(0, taxj - (taxs1 + taxs2))
        # return capped credit amount if eligible and have high min qinc
        return where(
            eligible & hi_min_qinc,
            min_(mpc_amount, p.marriage_penalty.maximum),
            0,
        )
