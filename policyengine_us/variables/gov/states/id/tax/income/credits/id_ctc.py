from policyengine_us.model_api import *


class id_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho child tax credit worksheet amount"
    documentation = (
        "Worksheet amount of the Idaho child tax credit. Idaho Code 63-3029L(1) "
        "allows the credit only for taxable years beginning before January 1, "
        "2026; from 2026 the nonrefundable credit list and the state child tax "
        "credit totals leave it out, so it applies only under a reform that "
        "revives it."
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID
    reference = (
        "https://legislature.idaho.gov/statutesrules/idstat/Title63/T63CH30/SECT63-3029L/",
        "https://taxsim.nber.org/historical_state_tax_forms/ID/2021/EIN00046_11-15-2021.pdf#page=10",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.id.tax.income.credits.ctc
        eligible_children = tax_unit("id_ctc_qualifying_children", period)
        # Multiply by the amount per child.
        return eligible_children * p.amount
