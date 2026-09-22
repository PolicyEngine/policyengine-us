Require explicit SPM measurement-universe status in datasets, keep SPM amounts, resources and poverty outcomes missing outside that universe, and return nullable floating-point poverty, equivalised-income and income-decile outputs.

Require Microdf 1.3.0 or later so weighted counts exclude missing SPM outcomes.

Fail closed when a dataset stores an SPM measurement-universe value the status enum does not define, instead of measuring that unit as outside the universe.
