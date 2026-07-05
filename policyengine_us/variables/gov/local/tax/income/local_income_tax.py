from policyengine_us.model_api import *


class local_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Local income tax"
    documentation = "Local income, wage, and earnings taxes."
    unit = USD

    # This variable is the SALT-deductible local income tax measure: it feeds
    # the federal SALT deduction via state_and_local_sales_or_income_tax, which
    # adds ["state_withheld_income_tax", "local_income_tax"].
    #
    # CONVENTION for cycle-inducing local taxes (a local tax that is itself a
    # function of state tax liability, which in turn depends on the federal SALT
    # deduction — putting such a tax directly in this `adds` list raises a
    # CycleError). Two patterns are accepted in this registry; pick deliberately
    # per locality:
    #   (a) Exclude from SALT. Levy the local tax only via
    #       local_income_tax_before_refundable_credits and leave it out of this
    #       list. Exact for non-itemizers; understates SALT (never understates
    #       federal tax) for itemizers. This is the Yonkers approach: the
    #       resident surcharge is a fraction of NY State tax, so it is levied in
    #       the pre-refundable aggregate but omitted here.
    #   (b) Withheld-estimate proxy. Where a state's withholding form combines
    #       state and local withholding (so a state-side withheld-tax estimate
    #       already carries the local component), route the local tax into SALT
    #       through state_withheld_income_tax instead of this list. Keeps
    #       itemizers' SALT roughly right at the cost of a small estimate error.
    #       This is the Maryland county-tax approach (#8888): county tax reaches
    #       SALT via md_withheld_income_tax (Form 502 combined MD + local
    #       withholding), not via this measure.
    # Non-cycle-inducing local taxes (e.g. Wilmington's flat earned income tax)
    # go directly in this list.
    adds = [
        "nyc_income_tax",
        "pa_philadelphia_wage_tax",
        "mo_kansas_city_earnings_tax",
        "mo_st_louis_earnings_tax",
        "de_wilmington_earned_income_tax",
    ]
