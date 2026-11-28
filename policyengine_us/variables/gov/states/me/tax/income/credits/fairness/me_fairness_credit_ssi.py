from policyengine_us.model_api import *


class me_fairness_credit_ssi(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = "Maine fairness credit SSI of the head and spouse"
    documentation = (
        "Supplemental security income the head and spouse receive, a payment "
        "under the federal Social Security Act (Schedule PTFC/STFC lines 1a "
        "and 2b). The credits use the claimant's individual income, or a "
        "married couple's joint income, so a tax unit dependent's SSI is the "
        "dependent's own."
    )
    definition_period = YEAR
    reference = (
        "https://legislature.maine.gov/statutes/36/title36sec5213-A.html",  # 1. B. (3)
        "https://legislature.maine.gov/statutes/36/title36sec5219-KK.html",  # 1. D. (3)
        # PDF pages 1, 4: .01(B) and (C), "individual income" and "joint
        # income", and .03, "the taxpayer's federal adjusted gross income".
        "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/Rule_813_May_2023.pdf#page=1",
        # Line 1a instructions, which line 2b points to.
        "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/25_1040me_sch_ptfc_fillable.pdf#page=3",
    )
    defined_for = StateCode.ME

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        filer = ~person("is_tax_unit_dependent", period)
        return tax_unit.sum(filer * add(person, period, ["ssi"]))
