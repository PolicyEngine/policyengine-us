from policyengine_us.model_api import *


class nv_liheap_energy_cost(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Nevada LIHEAP energy cost"
    documentation = (
        "Annual primary heating and electric energy costs used for the Fixed "
        "Annual Credit, less the annual service fee deduction Appendix A "
        "lists for the household's electricity and natural gas vendors. "
        "Section 507 leaves service fees out of the energy cost. Appendix A "
        "lists no dollar deduction for NV Energy, so for its customers, and "
        "for other or unreported vendors, a credit between the minimum and "
        "the cap can exceed the program's amount by up to that fee."
    )
    defined_for = StateCode.NV
    reference = (
        "https://www.leg.state.nv.us/nrs/nrs-702.html#NRS702Sec260",
        # PDF pages 37, 60, 112
        "https://dss.nv.gov/uploadedFiles/dwssnvgov/content/Energy/FY%202026%20EAP%20Manual%2008.2025%20ADA.pdf#page=37",
        # PDF pages 37, 60, 112
        "https://www.dss.nv.gov/contentassets/b3bcdb93ea2d4b3f8dc252451a34cbe4/2027-eap-state-manual--08.25.26-1.pdf#page=37",
    )

    def formula(spm_unit, period, parameters):
        # Annual bills, service fees included, stand in for the prior 12
        # months of vendor energy dollar usage. The primary heating bill and
        # the electricity bill are included; heating_expense already reads the
        # electricity bill when the home heats with electricity or solar, so
        # it is not added again.
        p = parameters(period).gov.states.nv.dwss.liheap.payment.vendor_deduction
        heating_type = spm_unit("heating_type", period)
        types = heating_type.possible_values
        electric_heat = (heating_type == types.ELECTRICITY) | (
            heating_type == types.SOLAR
        )
        heating = spm_unit("heating_expense", period)
        electricity = spm_unit("pre_subsidy_electricity_expense", period)
        # Each vendor's deduction comes off that vendor's bill only. The gas
        # bill is part of the energy cost only when gas heats the home.
        electricity_provider = spm_unit("nv_liheap_electricity_provider", period)
        gas_provider = spm_unit("nv_liheap_natural_gas_provider", period)
        gas_deduction = where(
            heating_type == types.NATURAL_GAS, p.natural_gas[gas_provider], 0
        )
        electricity_bill = where(electric_heat, heating, electricity)
        other_heating_bill = where(electric_heat, 0, max_(heating - gas_deduction, 0))
        return other_heating_bill + max_(
            electricity_bill - p.electricity[electricity_provider], 0
        )
