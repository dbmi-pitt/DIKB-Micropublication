# Copyright 2001 by Jeffrey Chang.  All rights reserved.
# This code is part of the Biopython distribution and governed by its
# license.  Please see the LICENSE file that should have been included
# as part of this package.

"""
Maximum Entropy code.

Uses Improved Iterative Scaling:
XXX ref

# XXX need to define terminology

"""
import math
from Numeric import *
from Bio import listfns

# XXX typecodes for Numeric
# XXX multiprocessor

MAX_IIS_ITERATIONS = 10000    # Maximum iterations for IIS.
IIS_CONVERGE = 1E-5           # Convergence criteria for IIS.
MAX_NEWTON_ITERATIONS = 100   # Maximum iterations on Newton's method.
NEWTON_CONVERGE = 1E-10       # Convergence criteria for Newton's method.

class MaxEntropy:
    """Holds information for a Maximum Entropy classifier.

    Members:
    classes      List of the possible classes of data.
    alphas       List of the weights for each feature.
    feature_fns  List of the feature functions.

    """
    def __init__(self):
        self.classes = []
        self.alphas = []
        self.feature_fns = []

def calculate(me, observation):
    """calculate(me, observation) -> list of log probs

    Calculate the log of the probability for each class.  me is a
    MaxEntropy object that has been trained.  observation is a vector
    representing the observed data.  The return value is a list of
    unnormalized log probabilities for each class.

    """
    scores = []
    for klass in range(len(me.classes)):
        lprob = 0.0
        for fn, alpha in map(None, me.feature_fns, me.alphas):
            lprob += fn(observation, klass) * alpha
        scores.append(lprob)
    return scores

def classify(me, observation):
    """classify(me, observation) -> class

    Classify an observation into a class.

    """
    scores = calculate(me, observation)
    max_score, klass = scores[0], me.classes[0]
    for i in range(1, len(scores)):
        if scores[i] > max_score:
            max_score, klass = scores[i], me.classes[i]
    return klass

def _eval_feature_fn(fn, xs, classes):
    """_eval_feature_fn(fn, xs, classes) -> dict of values

    Evaluate a feature function on every instance of the training set
    and class.  fn is a callback function that takes two parameters: a
    training instance and a class.  Return a dictionary of (training
    set index, class index) -> non-zero value.  Values of 0 are not
    stored in the dictionary.

    """
    values = {}
    for i in range(len(xs)):
        for j in range(len(classes)):
            f = fn(xs[i], classes[j])
            if f != 0:
                values[(i, j)] = f
    return values

def _calc_empirical_expects(xs, ys, classes, features):
    """_calc_empirical_expects(xs, ys, classes, features) -> list of expectations

    Calculate the expectation of each function from the data.  This is
    the constraint for the maximum entropy distribution.  Return a
    list of expectations, parallel to the list of features.

    """
    # E[f_i] = SUM_x,y P(x, y) f(x, y)
    #        = 1/N f(x, y)
    class2index = listfns.itemindex(classes)
    ys_i = [class2index[y] for y in ys]
    
    expect = []
    N = len(xs)
    for feature in features:
        s = 0
        for i in range(N):
            s += feature.get((i, ys_i[i]), 0)
        expect.append(float(s) / N)
    return expect

def _calc_model_expects(xs, classes, features, alphas):
    """_calc_model_expects(xs, classes, features, alphas) -> list of expectations.

    Calculate the expectation of each feature from the model.  This is
    not used in maximum entropy training, but provides a good function
    for debugging.

    """
    # SUM_X P(x) SUM_Y P(Y|X) F(X, Y)
    # = 1/N SUM_X SUM_Y P(Y|X) F(X, Y)
    p_yx = _calc_p_class_given_x(xs, classes, features, alphas)

    expects = []
    for feature in features:
        sum = 0.0
        for (i, j), f in feature.items():
            sum += p_yx[i][j] * f
        expects.append(sum/len(xs))
    return expects

def _calc_p_class_given_x(xs, classes, features, alphas):
    """_calc_p_class_given_x(xs, classes, features, alphas) -> matrix

    Calculate P(y|x), where y is the class and x is an instance from
    the training set.  Return a XSxCLASSES matrix of probabilities.

    """
    prob_yx = zeros((len(xs), len(classes)), Float32)

    # Calculate log P(y, x).
    for feature, alpha in map(None, features, alphas):
        for (x, y), f in feature.items():
            prob_yx[x][y] += alpha * f
    # Take an exponent to get P(y, x)
    prob_yx = exp(prob_yx)
    # Divide out the probability over each class, so we get P(y|x).
    for i in range(len(xs)):
        z = sum(prob_yx[i])
        prob_yx[i] = prob_yx[i] / z

    #prob_yx = []
    #for i in range(len(xs)):
    #    z = 0.0   # Normalization factor for this x, over all classes.
    #    probs = [0.0] * len(classes)
    #    for j in range(len(classes)):
    #        log_p = 0.0   # log of the probability of f(x, y)
    #        for k in range(len(features)):
    #            log_p += alphas[k] * features[k].get((i, j), 0.0)
    #        probs[j] = math.exp(log_p)
    #        z += probs[j]
    #    # Normalize the probabilities for this x.
    #    probs = map(lambda x, z=z: x/z, probs)
    #    prob_yx.append(probs)
    return prob_yx

def _calc_f_sharp(N, nclasses, features):
    """_calc_f_sharp(N, nclasses, features) -> matrix of f sharp values."""
    # f#(x, y) = SUM_i feature(x, y)
    f_sharp = zeros((N, nclasses))
    for feature in features:
        for (i, j), f in feature.items():
            f_sharp[i][j] += f
    return f_sharp

def _iis_solve_delta(N, feature, f_sharp, empirical, prob_yx):
    # Solve delta using Newton's method for:
    # SUM_x P(x) * SUM_c P(c|x) f_i(x, c) e^[delta_i * f#(x, c)] = 0
    delta = 0.0
    iters = 0
    while iters < MAX_NEWTON_ITERATIONS: # iterate for Newton's method
        f_newton = df_newton = 0.0       # evaluate the function and derivative
        for (i, j), f in feature.items():
            prod = prob_yx[i][j] * f * math.exp(delta * f_sharp[i][j])
            f_newton += prod
            df_newton += prod * f_sharp[i][j]
        f_newton, df_newton = empirical - f_newton / N, -df_newton / N

        ratio = f_newton / df_newton
        delta -= ratio
        if math.fabs(ratio) < NEWTON_CONVERGE:  # converged
            break
        iters = iters + 1
    else:
        raise "Newton's method did not converge"
    return delta

def _train_iis(xs, classes, features, f_sharp, alphas, e_empirical):
    # Do one iteration of hill climbing to find better alphas.
    # This is a good function to parallelize.

    # Pre-calculate P(y|x)
    p_yx = _calc_p_class_given_x(xs, classes, features, alphas)

    N = len(xs)
    newalphas = alphas[:]
    for i in range(len(alphas)):
        delta = _iis_solve_delta(N, features[i], f_sharp, e_empirical[i], p_yx)
        newalphas[i] += delta
    return newalphas


def train(training_set, results, feature_fns, update_fn=None):
    """train(training_set, results, feature_fns[, update_fn]) -> MaxEntropy object

    Train a maximum entropy classifier on a training set.
    training_set is a list of observations.  results is a list of the
    class assignments for each observation.  feature_fns is a list of
    the features.  These are callback functions that take an
    observation and class and return a 1 or 0.  update_fn is a
    callback function that's called at each training iteration.  It is
    passed a MaxEntropy object that encapsulates the current state of
    the training.
    
    """
    if not len(training_set):
        raise ValueError, "No data in the training set."
    if len(training_set) != len(results):
        raise ValueError, "training_set and results should be parallel lists."

    # Rename variables for convenience.
    xs, ys = training_set, results

    # Get a list of all the classes that need to be trained.
    classes = listfns.items(results)
    classes.sort()

    # Cache values for all features.
    features = [_eval_feature_fn(fn, training_set, classes)
                for fn in feature_fns]
    # Cache values for f#.
    f_sharp = _calc_f_sharp(len(training_set), len(classes), features)

    # Pre-calculate the empirical expectations of the features.
    e_empirical = _calc_empirical_expects(xs, ys, classes, features)

    # Now train the alpha parameters to weigh each feature.
    alphas = [0.0] * len(features)
    iters = 0
    while iters < MAX_IIS_ITERATIONS:
        nalphas = _train_iis(xs, classes, features, f_sharp,
                             alphas, e_empirical)
        diff = map(lambda x, y: math.fabs(x-y), alphas, nalphas)
        diff = reduce(lambda x, y: x+y, diff, 0)
        alphas = nalphas
        
        me = MaxEntropy()
        me.alphas, me.classes, me.feature_fns = alphas, classes, feature_fns
        if update_fn is not None:
            update_fn(me)
    
        if diff < IIS_CONVERGE:   # converged
            break
    else:
        raise "IIS did not converge"

    return me
