import re

def calculate_text(body):
    """
        Replace sum(1,2,3) to 6 and avg(1, 2, 3) to 2.0 
    """    
    for i in re.findall('\w*(sum\([\d,( )*]+\))\w*', body):
        sum = 0
        for j in re.findall('\d+', i):
            sum += int(j)
        body = body.replace(i, str(sum))
        
    for i in re.findall('\w*(avg\([\d,( )*]+\))\w*', body):
        sum = 0
        count = 0
        for j in re.findall('\d+', i):
            sum += int(j)
            count += 1
        body = body.replace(i, str(sum/float(count)))
    return body