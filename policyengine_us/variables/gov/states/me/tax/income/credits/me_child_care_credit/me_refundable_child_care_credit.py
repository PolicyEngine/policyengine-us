class me_refundable_child_care_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "ME Refundable Child Care Credit"
    unit = USD
    documentation = "Refundable portion of the ME Child Care Credit" 
    definition_period = YEAR
    reference = ("https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_1040me_sched_a_ff.pdf")

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.me.tax.income.credits.child_care
        maximum_refundable_credit = p.amount
        return min_(maximum_refundable_credit, tax_unit("me_child_care_credit",period))
