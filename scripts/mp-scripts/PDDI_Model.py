# PDDI_Model.py
#
# A simple model used to capture relevant values for PDDIs

## Author:
## Yifan Ning


## This code is licensed under Apache License Version 2.0, January
## 2004. Please see the license in the root folder of this project


## increase AUC
def getIncreaseAUCDict():

    assertEviD = getAssertionDict()

    increaseAucL = ["contVal", "numericVal", "numOfSubjects", "objectDose", "precipDose", "evidenceVal", "object", "precip"]
    for attr in increaseAucL:
        assertEviD[attr] = None

    return assertEviD


## inhibits, substrate of
def getAssertionDict():
    return { "objectURI": None, "valueURI": None,"assertType": None, "homepage":None, "label": None, 
             "evidence": None, "evidenceRole": None, "source":"DIKB",
             "evidenceType":None, "dateAnnotated":None, "whoAnnotated":None, "evidenceStatement": None, "evidenceSource": None, "researchStatementLabel": None,
             "asrt": None}
