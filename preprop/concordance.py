import os, sys, glob
from nilearn import masking
import numpy as np
import h5py
from scipy.stats import f,rankdata
import math

############ Kendall's W #####################################################
def IPN_kendallW(X):
    """
    Kendall's W
    X is 2D numpy-array (n*k ratings matrix)
    n is the number of objects and k is the number of judges.
    """
    [n, k] = np.shape(X)

    # if tiedrank ...
    R = np.zeros_like(X)
    for i in range(0, np.shape(X)[1]):   
        R[:,i] = rankdata(X[:,i])
    R_new = np.sort(np.round(R), axis=0)
    A = np.matlib.repmat(np.array(range(1,n+1)), k, 1).T
    T = np.sum(np.array((A-R_new), dtype=bool), axis=0) +1    
    RS = np.sum(R, axis=1)
    S = np.sum(np.square(RS)) - n * math.pow(np.mean(RS),2)
    F = k * k* (n * n * n-n)- k*np.sum(np.power(T, 3)-T)
    W = float(12)*S/F

    Fdist = W*(k-1) / (1-W)
    nu1 = n-1-(2/float(k));
    nu2 = nu1*(k-1);
    p = f.pdf(Fdist, nu1, nu2)

    return W, p, Fdist

############ Concordance Correlation Coefficient (CCC) ########################
def IPN_ssd(X):
    """
    X is a 1D array
    """
    R = len(X)
    ssd = 0
    for k in range(0, R):
        ssd = ssd + np.multiply((X[k+1:R] - X[k]) , (X[k+1:R] - X[k])).sum()
    return ssd

def IPN_ccc(Y):
    """
    Y is a 2D array, (N * R data matrix)
    REFERENCE:
    Lin, L.I. 1989. A Corcordance Correlation Coefficient to Evaluate
    Reproducibility. Biometrics 45, 255-268.

    """
    Ybar = np.mean(Y, axis=0) 
    S = np.cov(Y, rowvar=False, bias=True)
    R = np.shape(Y)[1]
    tmp = np.triu(S,1)
    rc = 2*tmp.ravel(order='F').sum() / ((R-1)*np.trace(S, 0) + IPN_ssd(Ybar))
    return rc

############ Interclass Correlation Coefficient (ICC) ########################
def IPN_icc(X, cse, typ):
    """
    Computes the interclass correlations for indexing the reliability analysis 
    according to shrout & fleiss' schema.

    INPUT:
    x   - ratings data matrix, data whose columns represent different
         ratings/raters & whose rows represent different cases or 
         targets being measured. Each target is assumed too be a random
         sample from a population of targets.
    cse - 1 2 or 3: 1 if each target is measured by a different set of 
         raters from a population of raters, 2 if each target is measured
         by the same raters, but that these raters are sampled from a 
         population of raters, 3 if each target is measured by the same 
         raters and these raters are the only raters of interest.
    typ - 'single' or 'k': denotes whether the ICC is based on a single
         measurement or on an average of k measurements, where 
         k = the number of ratings/raters.

    REFERENCE:
    Shrout PE, Fleiss JL. Intraclass correlations: uses in assessing rater
    reliability. Psychol Bull. 1979;86:420-428

    """     

    [n, k] = np.shape(X)
    
    # mean per target
    mpt = np.mean(X, axis=1)
    # mean per rater/rating
    mpr = np.mean(X, axis=0)
    # get total mean
    tm = np.mean(X)
    # within target sum sqrs
    tmp = np.square(X - np.matlib.repmat(mpt,k,1).T)
    WSS = np.sum(tmp)
    # within target mean sqrs
    WMS = float(WSS) / (n*(k - 1));
    # between rater sum sqrs
    RSS = np.sum(np.square(mpr - tm)) * n
    # between rater mean sqrs
    RMS = RSS / (float(k) - 1);
    # between target sum sqrs
    BSS = np.sum(np.square(mpt - tm)) * k
    # between targets mean squares
    BMS = float(BSS) / (n - 1)
    # residual sum of squares
    ESS = float(WSS) - RSS
    # residual mean sqrs
    EMS = ESS / ((k - 1) * (n - 1))

    if cse == 1:
        if typ == 'single':
            ICC = (BMS - WMS) / (BMS + (k - 1) * WMS)
        elif typ == 'k':
            ICC = (BMS - WMS) / BMS
        else:
            print "Wrong value for input type"
            sys.exit()

    elif cse == 2:
        if typ == 'single':
            ICC = (BMS - EMS) / (BMS + (k - 1) * EMS + k * (RMS - EMS) / n)
        elif typ == 'k':
            ICC = (BMS - EMS) / (BMS + (RMS - EMS) / n)
        else:
            print "Wrong value for input type"
            sys.exit()

    elif cse == 3:
        if typ == 'single':
            ICC = (BMS - EMS) / (BMS + (k - 1) * EMS)
        elif typ == 'k':
            ICC = (BMS - EMS) / BMS
        else:
            print "Wrong value for input type"
            sys.exit()

    else:
        print "Wrong value for input type"
        sys.exit()

    return ICC

