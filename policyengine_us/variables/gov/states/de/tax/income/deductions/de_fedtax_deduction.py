from policyengine_us.model_api import *


class de_fedtax_deduction(Variable):
    value_type = float
    entity = Person
    label = "Delaware deduction for selected components of federal income tax"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf#page=7"
        "https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf#page=11"
        "https://casetext.com/statute/delaware-code/title-30-state-taxes/part-ii-income-inheritance-and-estate-taxes/chapter-11-personal-income-tax/subchapter-ii-resident-individuals/section-1109-itemized-deductions-for-application-of-this-section-see-66-del-laws-c-86-section-8"
    )
    defined_for = StateCode.DE

    def formula(person, period, parameters):
        ustax = person.tax_unit("income_tax_before_refundable_credits", period)
        # correct ustax amount for flaw in CTC refundable/nonrefundable split
        ctc = parameters(period).gov.irs.credits.ctc
        ctc_fully_refundable = ctc.refundable.fully_refundable
        if ctc_fully_refundable:
            us_tax = ustax + person.tax_unit("non_refundable_ctc", period)
        else:
            us_tax = ustax
        # remove SECA and Additional Medicare taxes
        amtax = person.tax_unit("additional_medicare_tax", period)
        setax = add(person.tax_unit, period, ["self_employment_tax"])
        agg_tax = max_(0.0, us_tax - amtax - setax)
        # project agg_tax to head and spouse in net_tax variable
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        net_tax = (is_head | is_spouse) * agg_tax
        # prorate net_tax among head and spouse according to net incomes
        fraction = person("de_prorate_fraction", period)
        return fraction * net_tax
