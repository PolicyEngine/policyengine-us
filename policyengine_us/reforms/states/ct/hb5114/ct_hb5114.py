from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_ct_hb5114() -> Reform:
    class ct_hb5114_eligible(Variable):
        value_type = bool
        entity = TaxUnit
        label = "Eligible for Connecticut HB-5114 renter's tax credit"
        definition_period = YEAR
        defined_for = StateCode.CT
        reference = "https://www.cga.ct.gov/2026/TOB/H/PDF/2026HB-05114-R00-HB.PDF"

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.ct.hb5114

            # Must pay rent (assumed primary residence if paying rent in CT)
            rent = add(tax_unit, period, ["rent"])
            pays_rent = rent > 0

            # Must not be claimed as a dependent on another return
            head_is_dependent_elsewhere = tax_unit(
                "head_is_dependent_elsewhere", period
            )
            not_dependent = ~head_is_dependent_elsewhere

            # Income eligibility
            filing_status = tax_unit("filing_status", period)
            agi = tax_unit("adjusted_gross_income", period)
            income_threshold = p.income_threshold[filing_status]
            income_eligible = agi <= income_threshold

            return pays_rent & not_dependent & income_eligible

    class ct_hb5114_renters_credit(Variable):
        value_type = float
        entity = TaxUnit
        label = "Connecticut HB-5114 renter's tax credit"
        unit = USD
        definition_period = YEAR
        defined_for = "ct_hb5114_eligible"
        reference = "https://www.cga.ct.gov/2026/TOB/H/PDF/2026HB-05114-R00-HB.PDF"

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.ct.hb5114

            # Get annual rent paid
            rent = add(tax_unit, period, ["rent"])

            # Get federal AGI
            agi = tax_unit("adjusted_gross_income", period)

            # Credit = 20% of rent - 4% of AGI
            rent_portion = rent * p.rent_percentage
            agi_reduction = agi * p.agi_reduction_rate
            credit_amount = max_(rent_portion - agi_reduction, 0)

            # Apply maximum credit cap
            return min_(credit_amount, p.max_credit)

    def modify_parameters(parameters):
        # Add ct_hb5114_renters_credit to refundable credits list
        refundable = parameters.gov.states.ct.tax.income.credits.refundable
        current_refundable = refundable(instant("2027-01-01"))
        if "ct_hb5114_renters_credit" not in current_refundable:
            new_refundable = list(current_refundable) + ["ct_hb5114_renters_credit"]
            refundable.update(
                start=instant("2027-01-01"),
                stop=instant("2100-12-31"),
                value=new_refundable,
            )
        return parameters

    class reform(Reform):
        def apply(self):
            self.update_variable(ct_hb5114_eligible)
            self.update_variable(ct_hb5114_renters_credit)
            self.modify_parameters(modify_parameters)

    return reform


def create_ct_hb5114_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_ct_hb5114()

    p = parameters.gov.contrib.states.ct.hb5114

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ct_hb5114()
    else:
        return None


ct_hb5114 = create_ct_hb5114_reform(None, None, bypass=True)
