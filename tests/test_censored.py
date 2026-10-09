import numpy as np
import statsmodels.api as sm

from animas.censored import censored_regression


def _data(seed=0, n=400, censor_at=None):
    rng = np.random.default_rng(seed)
    x = rng.normal(size=n)
    y = 1.0 + 2.0 * x + rng.normal(scale=1.0, size=n)
    X = np.column_stack([np.ones(n), x])
    cens = np.zeros(n, dtype=bool)
    if censor_at is not None:
        cens = y < censor_at
        y = np.where(cens, censor_at, y)
    return y, X, cens


def test_recovers_parameters_with_censoring():
    y, X, cens = _data(censor_at=0.5)
    assert 0.2 < cens.mean() < 0.5
    fit = censored_regression(y, X, cens, names=["a", "b"], hac_lags=0)
    assert fit.converged
    assert abs(fit.coef("a") - 1.0) < 0.2
    assert abs(fit.coef("b") - 2.0) < 0.2
    assert abs(fit.sigma - 1.0) < 0.15
    # substitution at the limit is biased for the same data
    naive = np.linalg.lstsq(X, y, rcond=None)[0]
    assert abs(naive[1] - 2.0) > abs(fit.coef("b") - 2.0)


def test_no_censoring_matches_ols_newey_west():
    y, X, cens = _data(seed=1)
    fit = censored_regression(y, X, cens, names=["a", "b"], hac_lags=6)
    ols = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": 6, "use_correction": False})
    assert np.allclose(fit.params, ols.params, atol=1e-8)
    assert np.allclose(fit.se, ols.bse, rtol=1e-4)


def test_ci_and_pvalue_shape():
    y, X, cens = _data(seed=2, censor_at=0.0)
    fit = censored_regression(y, X, cens, names=["a", "b"])
    lo, hi = fit.ci("b")
    assert lo < 2.0 < hi
    assert 0 <= fit.pvalue("b") < 1e-6
