from policyengine_us.model_api import *


class ms_liheap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Mississippi LIHEAP regular heating assistance"
    documentation = (
        "Verified for FY2026. Earlier years use model parameter backfilling "
        "and are unverified historical estimates."
    )
    defined_for = "ms_liheap_eligible"
    reference = "https://www.sos.ms.gov/adminsearch/ACCode/00000693c.pdf#page=24,36,37,39,58,59,60,61,62,63,64"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ms.mdhs.liheap
        size = spm_unit("ms_liheap_household_size", period)
        income = spm_unit("ms_liheap_income", period)
        # Rule 7.8 A directs use of the attached matrix (PDF pp. 59-64). Neither
        # the manual nor FY2026 plan section 2.5 defines 25% FPG bands or rounding.
        # That numerical pattern is not an authorized replacement: the matrix
        # prints $31,313 for size 3, five bands for size 8, and four for size 12.
        band = 0
        for table_size in range(1, int(p.maximum_table_size) + 1):
            band = where(
                size == table_size,
                p.income_bands[str(table_size)].calc(income, right=True),
                band,
            )
        fuel = spm_unit("heating_type", period)
        types = fuel.possible_values
        # Shared cap parameters reproduce the published progression without copying
        # dollar amounts for every household size. Preserve the anomalous size-16
        # propane cell; agency clarification is needed before correcting the source.
        cap = p.maximum_payment[fuel] - max_(band - 1, 0) * p.payment_reduction[fuel]
        exception = (
            (fuel == types.PROPANE)
            & (size == p.propane_exception_household_size)
            & (band == p.propane_exception_income_band)
        )
        cap = where(exception, p.propane_exception_amount, cap)
        # Rule 7.8 D gives electric-heating households the total-electric annual cap.
        # Only the main heating bill is counted here: no additional cooling/electric
        # allowance for a non-electric heating household. Prior awards consuming the
        # shared annual cap, per-delivery propane limits, and prepaid-account rules
        # are not represented. Annual heating expenses approximate eligible bills.
        expense = max_(spm_unit("heating_expense", period), 0)
        # Heat in rent with no specified charge receives $100 per intake under 6.4 B;
        # charge documentation/intake counts cannot be inferred, so that pathway is
        # not modeled. Source gaps (sizes 11/15 and upper ranges for 10/18/20) and
        # sizes above 20 also return zero as coverage gaps, not legal ineligibility.
        return where(band > 0, min_(cap, expense), 0)
