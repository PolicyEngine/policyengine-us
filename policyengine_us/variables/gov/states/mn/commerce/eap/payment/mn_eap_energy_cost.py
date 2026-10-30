from policyengine_us.model_api import *


class mn_eap_energy_cost(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Minnesota EAP annual energy cost"
    defined_for = StateCode.MN
    reference = (
        # PDF pages 117-119, 125-126
        "https://mn.gov/commerce-stat/pdfs/ffy26-eap-policy-manual.pdf#page=117",
        # PDF pages 119-121, 127-128
        "https://mn.gov/commerce-stat/pdfs/ffy27-eap-policy-manual.pdf#page=119",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/MN_BenefitMatrix_2026.xlsx",
        "https://mn.gov/commerce-stat/xls/phb-calculator.xlsx",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mn.commerce.eap.payment
        # Households paying their own energy use the total of all home energy
        # bills, heating fuels and all electricity. Current-year expenses stand
        # in for prior-year consumption; the eHEAT larger-of rule for partial
        # data and lower-of rule for business use or shared meters are not
        # modeled. Zero expense inputs mean no cost, so the backup-matrix
        # fallback for an own-payer without consumption data is not modeled.
        own_cost = add(spm_unit, period, p.energy_cost_sources)
        electricity = spm_unit("pre_subsidy_electricity_expense", period)
        heating_type = spm_unit("heating_type", period)
        types = heating_type.possible_values
        housing = spm_unit("mn_eap_housing_type", period)
        # Heat included in rent uses the backup matrix for the primary fuel and
        # housing type. No heating_type value identifies steam, district
        # heating or metered propane, so those rows are not selected; wood,
        # coal, solar and other fuels have no row.
        backup_cost = select(
            [
                (heating_type == types.FUEL_OIL) | (heating_type == types.KEROSENE),
                heating_type == types.PROPANE,
                heating_type == types.NATURAL_GAS,
                heating_type == types.ELECTRICITY,
            ],
            [
                p.backup_cost.oil[housing],
                p.backup_cost.propane[housing],
                p.backup_cost.natural_gas[housing],
                p.backup_cost.electricity[housing],
            ],
            default=0,
        )
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        # Section 8, public or tribal subsidized housing with heat in rent bases
        # the benefit on electric costs.
        subsidized = spm_unit(
            "receives_housing_assistance", period
        ) | spm_unit.household("is_in_public_housing", period)
        rent_cost = where(subsidized, electricity, backup_cost)
        return where(heat_in_rent, rent_cost, own_cost)
