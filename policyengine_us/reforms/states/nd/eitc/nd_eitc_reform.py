from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_nd_eitc() -> Reform:
    class nd_eitc(Variable):
        value_type = float
        entity = TaxUnit
        label = "North Dakota Earned Income Tax Credit"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.ND

        def formula(tax_unit, period, parameters):
            p = parameters(
                period
            ).gov.contrib.states.nd.child_poverty_impact_dashboard.eitc
            federal_eitc = tax_unit("eitc", period)
            return federal_eitc * p.match

    class nd_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "North Dakota refundable income tax credits"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/form-nd-1-2021.pdf",
            "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/individual-income-tax-booklet-2021.pdf",
            "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/form-nd-1-2022.pdf",
            "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/2022-individual-income-tax-booklet.pdf",
        )
        defined_for = StateCode.ND

        def formula(tax_unit, period, parameters):
            return tax_unit("nd_eitc", period)

    class reform(Reform):
        def apply(self):
            self.update_variable(nd_eitc)
            self.update_variable(nd_refundable_credits)

    return reform


def create_nd_eitc_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_nd_eitc()

    p = parameters.gov.contrib.states.nd.child_poverty_impact_dashboard.eitc

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        p_at_period = p(current_period)
        if p_at_period.in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_nd_eitc()
    else:
        return None


nd_eitc = create_nd_eitc_reform(None, None, bypass=True)
