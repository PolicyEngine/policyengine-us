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
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        aggregate_tax = (is_head | is_spouse) * (
            person.tax_unit("income_tax_before_refundable_credits", period)
            - person.tax_unit("additional_medicare_tax", period)
        )
        # prorate aggregate_tax among head and spouse according to net incomes
        net_income = person("ia_net_income", period)
        fraction = person("ia_prorate_fraction", period)
        prorated_tax = fraction * aggregate_tax
        # allocate any dependent self-employment tax to tax unit head
        indiv_setax = person("self_employment_tax", period)
        is_dependent = person("is_tax_unit_dependent", period)
        sum_dep_setax = person.tax_unit.sum(is_dependent * indiv_setax)
        setax = ~is_dependent * indiv_setax + is_head * sum_dep_setax
        # return prorated_tax less setax
        return max_(0, prorated_tax - setax)
