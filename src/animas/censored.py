"""Left-censored (Tobit-style) regression with a Newey-West HAC sandwich.

Model: y* = X beta + e, e ~ N(0, sigma^2). For uncensored rows y = y*; for censored
rows only y* <= lower is known. With no censored rows the estimator is ordinary least
squares (sigma is the maximum-likelihood value) and the sandwich reduces to the
Newey-West covariance for beta.

Rows must be in time order: the HAC kernel is applied along the observation index,
which is the honest choice for an unevenly sampled series (the lag is "observations",
not months).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy import optimize, stats

Z95 = 1.959963984540054


@dataclass
class Fit:
    names: list[str]
    params: np.ndarray
    se: np.ndarray
    cov: np.ndarray
    sigma: float
    loglik: float
    n: int
    n_censored: int
    hac_lags: int
    converged: bool
    fitted: np.ndarray = field(repr=False, default=None)

    def coef(self, name: str) -> float:
        return float(self.params[self.names.index(name)])

    def stderr(self, name: str) -> float:
        return float(self.se[self.names.index(name)])

    def ci(self, name: str) -> tuple[float, float]:
        b, s = self.coef(name), self.stderr(name)
        return b - Z95 * s, b + Z95 * s

    def pvalue(self, name: str) -> float:
        b, s = self.coef(name), self.stderr(name)
        if s == 0 or not np.isfinite(s):
            return float("nan")
        return float(2 * stats.norm.sf(abs(b / s)))


def _unpack(theta: np.ndarray, p: int) -> tuple[np.ndarray, float]:
    return theta[:p], float(np.exp(theta[p]))


def _negloglik(theta, X, y, cens):
    p = X.shape[1]
    beta, sigma = _unpack(theta, p)
    mu = X @ beta
    z = (y - mu) / sigma
    ll_unc = stats.norm.logpdf(z[~cens]) - np.log(sigma)
    ll_cen = stats.norm.logcdf(z[cens])
    return -(ll_unc.sum() + ll_cen.sum())


def _scores(theta, X, y, cens) -> np.ndarray:
    """Per-observation gradient of the log-likelihood wrt (beta, log sigma)."""
    p = X.shape[1]
    beta, sigma = _unpack(theta, p)
    mu = X @ beta
    z = (y - mu) / sigma
    s = np.zeros((len(y), p + 1))
    u = ~cens
    s[u, :p] = X[u] * (z[u] / sigma)[:, None]
    s[u, p] = z[u] ** 2 - 1.0
    if cens.any():
        w = z[cens]
        lam = np.exp(stats.norm.logpdf(w) - stats.norm.logcdf(w))  # phi/Phi, stable
        s[cens, :p] = -X[cens] * (lam / sigma)[:, None]
        s[cens, p] = -lam * w
    return s


def _grad(theta, X, y, cens):
    return -_scores(theta, X, y, cens).sum(axis=0)


def _num_hessian(theta, X, y, cens, h: float = 1e-5) -> np.ndarray:
    """Observed information (negative Hessian of the log-likelihood), central differences."""
    k = len(theta)
    H = np.zeros((k, k))
    for j in range(k):
        e = np.zeros(k)
        e[j] = h
        H[:, j] = (_grad(theta + e, X, y, cens) - _grad(theta - e, X, y, cens)) / (2 * h)
    return 0.5 * (H + H.T)


def hac_meat(scores: np.ndarray, lags: int) -> np.ndarray:
    """Newey-West (Bartlett kernel) long-run covariance of the score sequence."""
    S = scores.T @ scores
    n = len(scores)
    for lag in range(1, min(lags, n - 1) + 1):
        w = 1.0 - lag / (lags + 1.0)
        G = scores[lag:].T @ scores[:-lag]
        S += w * (G + G.T)
    return S


def censored_regression(
    y: np.ndarray,
    X: np.ndarray,
    censored: np.ndarray,
    *,
    names: list[str] | None = None,
    hac_lags: int = 12,
) -> Fit:
    """Fit y* = X beta + e with left-censoring; HAC covariance along the row order.

    For censored rows `y` holds the censoring threshold (the reporting limit on the
    model scale). `hac_lags=0` gives the plain (heteroskedasticity-robust) sandwich.
    """
    y = np.asarray(y, dtype=float)
    X = np.asarray(X, dtype=float)
    cens = np.asarray(censored, dtype=bool)
    n, p = X.shape
    if names is None:
        names = [f"b{i}" for i in range(p)]
    if n <= p + 1:
        raise ValueError(f"too few rows ({n}) for {p} parameters")
    if cens.sum() >= n - p:
        raise ValueError("almost every row is censored; the model is not identified")

    # Start from OLS treating thresholds as values.
    beta0, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid0 = y - X @ beta0
    theta0 = np.append(beta0, np.log(max(resid0.std(), 1e-6)))
    converged = True
    if cens.any():
        res = optimize.minimize(
            _negloglik, theta0, args=(X, y, cens), jac=_grad, method="BFGS",
            options={"gtol": 1e-8, "maxiter": 2000},
        )
        theta = res.x
        converged = bool(res.success)
    else:
        sigma_ml = np.sqrt((resid0**2).mean())
        theta = np.append(beta0, np.log(sigma_ml))
    scores = _scores(theta, X, y, cens)
    H = _num_hessian(theta, X, y, cens)
    Hinv = np.linalg.pinv(H)
    meat = hac_meat(scores, hac_lags) if hac_lags > 0 else scores.T @ scores
    cov = Hinv @ meat @ Hinv
    beta, sigma = _unpack(theta, p)
    se = np.sqrt(np.clip(np.diag(cov)[:p], 0, None))
    return Fit(
        names=list(names), params=beta, se=se, cov=cov[:p, :p], sigma=sigma,
        loglik=float(-_negloglik(theta, X, y, cens)), n=int(n), n_censored=int(cens.sum()),
        hac_lags=int(hac_lags), converged=converged, fitted=X @ beta,
    )
