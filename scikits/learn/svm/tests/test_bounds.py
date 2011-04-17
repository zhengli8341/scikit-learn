import numpy as np
from scipy import sparse as sp

from scikits.learn.svm.bounds import l1_min_c
from scikits.learn.svm import LinearSVC
from scikits.learn.linear_model.logistic import LogisticRegression
from scikits.learn.svm.sparse import LinearSVC as SparseSVC
from scikits.learn.linear_model.sparse.logistic import LogisticRegression as \
                                                       SparseLogRegression


dense_X = [[-1, 0], [0, 1], [1, 1], [1, 1]]
sparse_X = sp.csr_matrix(dense_X)

Y1 = [0, 1, 1, 1]
Y2 = [2, 1, 0, 0]


def test_l1_min_c():
    losses = ['l2', 'log']
    Xs = {'sparse': sparse_X, 'dense': dense_X}
    Ys = {'two-classes': Y1, 'multi-class': Y2}
    intercepts = {'no-intercept':  {'fit_intercept': False},
                  'fit-intercept': {'fit_intercept': True,
                                    'intercept_scaling': 10}}

    for loss in losses:
        for X_label, X in Xs.items():
            for Y_label, Y in Ys.items():
                for intercept_label, intercept_params in intercepts.items():
                    desc = 'Test l1_min_c loss=%r %s %s %s' % \
                           (loss, X_label, Y_label, intercept_label)
                    check = lambda X, Y, loss, intercept_ps: \
                                   check_l1_min_c(X, Y, loss, **intercept_ps)
                    check.description = desc
                    yield check, X, Y, loss, intercept_params


def check_l1_min_c(X, y, loss, fit_intercept=True, intercept_scaling=None):
    min_c = l1_min_c(X, y, loss, fit_intercept, intercept_scaling)

    clf = {
        ('log', False): LogisticRegression(penalty='l1'),
        ('log', True):  SparseLogRegression(penalty='l1'),
        ('l2', False):  LinearSVC(loss='l2', penalty='l1', dual=False),
        ('l2', True):   SparseSVC(loss='l2', penalty='l1', dual=False),
    }[loss, sp.issparse(X)]

    clf.fit_intercept = fit_intercept
    if clf.intercept_scaling is not None:
        clf.intercept_scaling = intercept_scaling

    clf.C = min_c
    clf.fit(X, y)
    assert (np.asanyarray(clf.coef_) == 0).all()
    assert (np.asanyarray(clf.intercept_) == 0).all()

    clf.C = min_c * 1.01
    clf.fit(X, y)
    assert (np.asanyarray(clf.coef_) != 0).any() or \
           (np.asanyarray(clf.intercept_) != 0).any()
