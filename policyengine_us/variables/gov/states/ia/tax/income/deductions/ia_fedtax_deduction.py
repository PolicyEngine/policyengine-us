from policyengine_us.model_api import *


class ia_fedtax_deduction(Variable):
    value_type = float
    entity = Person
    label = "Iowa deduction for selected components of federal income tax"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf#page=41"
        "https://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf#page=41"
    )
    defined_for = StateCode.IA

    def formula(person, period, parameters):
        # Iowa allows a deduction of federal income taxes from Iowa net
        # income, but federal payroll taxes (FICA and SECA and Additional
        # Medicare) cannot be used to reduced Iowa net income.
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
        fraction = person("ia_prorate_fraction", period)
        return fraction * net_tax
