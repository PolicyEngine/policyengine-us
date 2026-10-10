from policyengine_us.model_api import *


class id_health_insurance_premiums_medical_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Claimant medical deduction for Idaho health premium subtraction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID
    reference = (
        "https://legislature.idaho.gov/statutesrules/idstat/Title63/T63CH30/SECT63-3022P/",
        # PDF pages 48-49 (Form 39R, line 18 and worksheet lines 1-8).
        "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_03-02-2026.pdf#page=48",
        "https://www.irs.gov/instructions/i1040sca",
    )
    documentation = (
        "Medical deduction used to allocate the claimant's health premium "
        "overlap. Only costs paid by the head and spouse enter the medical "
        "floor calculation, including their payments covering dependents. "
        "Premiums excluded or deducted elsewhere are removed first. The "
        "actual federal medical deduction limits the derived result. A "
        "federal medical deduction or expense subtotal supplied for this "
        "period represents the claimant's actual Schedule A amounts and is "
        "honored even when its underlying expenses are not represented in "
        "person inputs. A supplied Schedule A expense subtotal already "
        "excludes pretax premiums and premiums deducted on Schedule 1."
    )

    def formula(tax_unit, period, parameters):
        # Actual Schedule A deductions and expense subtotals are authoritative.
        # Subtotals already exclude pretax and Schedule 1 premiums, so do not
        # remove those amounts again. Check the source before calculation:
        # cached results and other periods or branches do not describe this claim.
        supplied_medical = any(
            has_input_for_period(tax_unit.simulation, variable, period)
            for variable in (
                "medical_expense_deduction",
                "itemized_medical_expenses",
            )
        )
        federal_medical = max_(0, tax_unit("medical_expense_deduction", period))
        if supplied_medical:
            return federal_medical
        premiums = tax_unit("id_qualified_health_insurance_premiums", period)
        other_medical = tax_unit_non_dep_add(
            tax_unit, period, ["other_medical_expenses"]
        )
        p = parameters(period).gov.irs.deductions.itemized.medical
        medical_floor = p.floor * tax_unit("positive_agi", period)
        # Form 39R lines 1-6 use costs claimed on this return, not payments
        # independently made by dependents and aggregated by the federal model.
        claimant_medical = max_(0, premiums + other_medical - medical_floor)
        return min_(federal_medical, claimant_medical)
