from policyengine_us.model_api import *


def create_nc_cdcc() -> Reform:
    class nc_cdcc(Variable):
        value_type = float
        entity = TaxUnit
        label = "North Carolina CDCC"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.NC

        def formula(tax_unit, period, parameters):
            cdcc = tax_unit("cdcc", period)
            p = parameters(period).gov.contrib.states.nc.cdcc
            base_credit = p.match * cdcc
            joint = tax_unit("tax_unit_is_joint", period)
            income = tax_unit("adjusted_gross_income", period)
            reduction = where(joint, p.phase_out.joint.calc(income), p.phase_out.single.calc(income))
            return max_(base_credit - reduction, 0)


#TODO: add the net income tree

    class reform(Reform):
        def apply(self):
            self.update_variable(nc_cdcc)

    return reform


def create_nc_cdcc_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_nc_cdcc()

    p = parameters(period).gov.contrib.states.nc.cdcc

    if p.in_effect:
        return create_nc_cdcc()
    else:
        return None


nc_cdcc = create_nc_cdcc_reform(
    None, None, bypass=True
)
