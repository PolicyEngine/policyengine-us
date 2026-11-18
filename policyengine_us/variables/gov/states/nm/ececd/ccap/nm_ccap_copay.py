from policyengine_us.model_api import *


class nm_ccap_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = MONTH
    label = "New Mexico CCAP family copayment"
    defined_for = StateCode.NM
    reference = (
        "https://www.nmececd.org/wp-content/uploads/2024/09/CCA-Co-payments-waived_rev1l.pdf#page=1",
        "https://www.nmlegis.gov/handouts/ALFC%20120825%20Item%208%20Policy%20Brief%20Child%20Care%20Update.pdf#page=2",
        "https://www.srca.nm.gov/parts/title08/08.015.0002.html",
        "https://www.srca.nm.gov/parts/title08/08.009.0003.html",
        "https://www.nmececd.org/wp-content/uploads/2025/11/8.9.3_integrated_FULL-TEXT.pdf#page=13",
        # PDF pages 12-13
        "https://prod-rf-lambda.rtssaas.com/PublicFiles/d89c47bd0d70402dba89b03a22bda6d1/b0e207a9-a1a3-412d-9660-0a6e925f6f25/8.9.3.pdf#page=12",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nm.ececd.ccap.copay
        # The copay is $0 for every modeled period, but for different reasons
        # across three eras (LFC Policy Brief, Dec 9 2025, p.2):
        #   - copay.waived is true (2022-05-01 to 2023-06-30, and 2025-11-01
        #     onward under Universal Child Care): all copays waived -> $0.
        #     8.9.3.13.E NMAC (amended 2025-11-04) states that copayments are
        #     waived; from 2026-09-09, 8.9.3.12 and 8.9.3.14 NMAC require
        #     copayments only after a fiscal trigger and not before 2027-03-01.
        #   - copay.waived is false and period >= 2023-07-01: the copay was
        #     reinstated only for families above 200% FPL, using the annually
        #     published copay schedule (8.9.3.24 NMAC; from 2023-08-01 the
        #     percent-of-income chart in 8.9.3.13.D) that is not encoded, so
        #     that partial reinstatement is APPROXIMATED as $0 here.
        #   - copay.waived is false and period < 2022-05-01: the pre-2022 copay
        #     formula (8.15.2.13.B) is likewise not modeled -> $0.
        # When the published copay schedule is encoded, the false branch should
        # compute the >200% FPL copay instead of returning zero.
        if p.waived:
            return 0
        return 0
