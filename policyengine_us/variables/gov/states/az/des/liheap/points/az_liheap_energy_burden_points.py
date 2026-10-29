from policyengine_us.model_api import *


class az_liheap_energy_burden_points(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Arizona LIHEAP energy burden points"
    documentation = (
        "Benefit matrix points from energy cost as a share of countable income "
        "(5% or less gives 0 points, then one point per five-percent band up to "
        "6 points at 31% or over), plus 2 points for portable fuel heating "
        "(propane, wood or coal). A positive cost with no income takes the top "
        "band; no cost gives no burden points."
    )
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/AZ_BenefitMatrix_Heating_2026.pdf#page=1",
        "https://des.az.gov/liheap",
        # PDF pages 5, 10, 40
        "https://des.az.gov/sites/default/files/dl/CCSD-LIHEAP-Policy.pdf#page=5",
    )
    defined_for = StateCode.AZ

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.az.des.liheap.points
        cost = spm_unit("az_liheap_energy_cost", period)
        income = spm_unit("az_liheap_countable_income", period)
        # Worksheet: "Total Monthly Cost ÷ 30 Days Gross Income = % Energy
        # Burden"; annual over annual gives the same ratio. The worksheet does
        # not address zero income: a positive cost with no income is an
        # unbounded burden and takes the top band, and no cost is no burden.
        # The quotient is formed in float64 so that an exact band top such as
        # 2,400 / 24,000 = 0.10 stays in its band.
        burden = np.divide(
            cost.astype(np.float64),
            income,
            out=np.full(cost.shape, np.inf),
            where=income > 0,
        )
        burden = where(cost > 0, burden, 0)
        # "5% or less" is 0 points and the DES example places 17.5% in the
        # "16% - 20%" band, so right=True with the -inf first threshold.
        burden_points = p.energy_burden.calc(burden, right=True)
        # Worksheet: "Note: Add 2 points for portable fuels". "Portable Fuel:
        # Energy that is derived from propane, wood, coal, fuel for gas
        # generators, and/or pellets" (page 5); generator fuel and pellets have
        # no heating type of their own, and fuel oil and kerosene are not
        # portable fuels under this definition.
        heating_type = spm_unit("heating_type", period)
        types = heating_type.possible_values
        portable_fuel = (
            (heating_type == types.PROPANE)
            | (heating_type == types.WOOD)
            | (heating_type == types.COAL)
        )
        return burden_points + where(portable_fuel, p.portable_fuel, 0)
