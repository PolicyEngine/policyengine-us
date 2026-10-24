from policyengine_us.model_api import *


class ia_fedtax_deduction(Variable):
    value_type = float
    entity = Person
    label = "Iowa deduction for selected components of federal income tax"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdf",
        "https://revenue.iowa.gov/media/2650/download?inline#page=40",
        "https://revenue.iowa.gov/media/2650/download?inline#page=41",
        "https://revenue.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdf",
        "https://revenue.iowa.gov/media/2721/download?inline#page=40",
        "https://revenue.iowa.gov/media/2721/download?inline#page=41",
    )
    defined_for = StateCode.IA

    def formula(person, period, parameters):
        # Iowa deducts the federal tax paid (IA 1040 line 31) and adds back
        # on line 28 the federal 1040 Schedule 2 taxes those payments also
        # covered, among them self-employment tax (line 4), additional Social
        # Security and Medicare tax (line 7), additional tax on IRAs and other
        # tax-favored accounts (line 8), Additional Medicare tax (line 11) and
        # other additional taxes (line 18); the net investment income tax
        # (line 12) is not added back. With payments equal to the liability,
        # the deduction is the federal income tax without the added-back taxes.
        ustax = person.tax_unit("income_tax_before_refundable_credits", period)
        # Retain the existing addback in fully refundable years, including
        # any nonrefundable credit for other dependents in 2021.
        ctc = parameters(period).gov.irs.credits.ctc
        ctc_fully_refundable = ctc.refundable.fully_refundable
        if ctc_fully_refundable:
            us_tax = ustax + person.tax_unit("non_refundable_ctc", period)
        else:
            us_tax = ustax
        # income_tax_before_refundable_credits never includes the
        # self-employment or Additional Medicare tax, so only the added-back
        # Schedule 2 taxes it does include are removed.
        added_back = add(
            person.tax_unit,
            period,
            [
                "unreported_payroll_tax",
                "qualified_retirement_penalty",
                "recapture_of_investment_credit",
            ],
        )
        agg_tax = max_(0.0, us_tax - added_back)
        # project agg_tax to head and spouse in net_tax variable
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        net_tax = (is_head | is_spouse) * agg_tax
        # prorate net_tax among head and spouse according to net incomes
        fraction = person("ia_prorate_fraction", period)
        return fraction * net_tax
