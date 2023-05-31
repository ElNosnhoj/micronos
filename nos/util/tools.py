#===================================================================
# file: tools.py
# desc: some common helpers 
# dev : nos
#===================================================================
import time

class CTO_TIMEOUT(Exception): pass

def isClass(c):
    return type(CTO_TIMEOUT)==type(c)
def ConditionTimeout(fn,to=5.0,exception=None):
    start = time.time()
    while time.time() - start <= to:
        if fn(): return True
        
    if exception==None: return False
    
    if issubclass(exception,Exception): raise exception
    else: raise Exception("exception provided is not an exception")
CTO=ConditionTimeout

def between(val,low,high):
    """ checks if value between 2 numbers
    * val (`number`): value to be checked
    * low (`number`): minimum value
    * high(`number`): maximum value
    return (`bool`) : true if between low and high
    """
    if val>=low and val<=high: return True
    else: return False
    
def maprange(x,a,b,c,d):
    """ maps x in range a->b to range c->d
    * x (`number`): input value to be converted
    * a (`number`): minimum input range
    * b (`number`): maximum input range
    * c (`number`): minimum output range
    * d (`number`): maximum output range
    """
    return (x-a)/(b-a)*(d-c)+c