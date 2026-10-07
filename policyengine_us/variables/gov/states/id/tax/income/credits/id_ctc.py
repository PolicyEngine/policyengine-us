from policyengine_us.model_api import *


class id_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho Child Tax Credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID
    reference = (
        "https://legislature.idaho.gov/statutesrules/idstat/Title63/T63CH30/SECT63-3029L/",
        "https://taxsim.nber.org/historical_state_tax_forms/ID/2021/EIN00046_11-15-2021.pdf#page=10",
    )

    def formula(tax_unit, period, parameters):
        # Get relevant parameter subtree.
        p = parameters(period).gov.states.id.tax.income.credits.ctc
        # "the term "qualifying child" has the meaning as defined in section 24(c) of the Internal Revenue Code."
        # IRC 24(c) defines eligible children under the federal CTC. Its age
        # test is under 17; the 2021 federal expansion to age 17 is in IRC
        # 24(i)(1), so Idaho does not count those children in 2021.
        person = tax_unit.members
        over_age = person("ctc_qualifying_child", period) & (
            person("age", period) >= p.ineligible_age
        )
        eligible_children = tax_unit("ctc_qualifying_children", period) - tax_unit.sum(
            over_age
        )
        # Multiply by the amount per child.
        return eligible_children * p.amount
