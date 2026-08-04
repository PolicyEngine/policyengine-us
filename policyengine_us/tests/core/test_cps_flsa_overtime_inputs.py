import numpy as np

from policyengine_us.data.cps import (
    CPS_FLSA_EXECUTIVE_ADMINISTRATIVE_PROFESSIONAL_OCCUPATION_CODES,
    CPS_FLSA_OVERTIME_OCCUPATION_CODES,
)


def test_cps_flsa_overtime_occupation_codes_are_public_inputs():
    assert CPS_FLSA_OVERTIME_OCCUPATION_CODES == {
        "has_never_worked": 53,
        "is_military": 52,
        "is_computer_scientist": 8,
        "is_farmer_fisher": 41,
    }
    np.testing.assert_array_equal(
        CPS_FLSA_EXECUTIVE_ADMINISTRATIVE_PROFESSIONAL_OCCUPATION_CODES,
        np.array(
            [
                1,
                2,
                3,
                5,
                6,
                7,
                9,
                10,
                11,
                12,
                13,
                14,
                15,
                16,
                18,
                19,
                25,
                26,
                27,
                28,
                29,
                34,
                36,
                38,
                39,
                40,
                42,
                50,
            ],
            dtype=np.int16,
        ),
    )
