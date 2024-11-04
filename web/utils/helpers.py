""" function is_active(endpoint) {
        return request.endpoint === endpoint || request.endpoint.startsWith(endpoint + '.');
    }  """
from flask import request

# Custom function definition
def is_active(*endpoints):
    #return any(request.endpoint == endpoint or request.endpoint.startswith(endpoint + '.') for endpoint in endpoints)
    return any(request.endpoint == endpoint or request.endpoint.endswith('.' + endpoint) for endpoint in endpoints)

""" ============================================ """
def find_dept_by_name(d):
    if d == 'k':
        d = 'kitchen'
    elif d == 'c':
        d = 'cocktails'
    elif d == 'b':
        d = 'bar'
    else:
        d = 'invalid department'
    return d
    
""" ================================== """
def categ(categories):
    category = { 
        #0: { 'id': 0, 'parent': 0, 'name': "Root node", 'sub': [] }
    }

    category = {}
    for c in categories:
        category.setdefault(c['parent'], { 'sub': [] })
        category.setdefault(c['id'], { 'sub': [] })
        category[c['id']].update(c)
        category[c['parent']]['sub'].append(category[c['id']])

    return category

""" ================================== """
def user_ip():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        ip =  request.environ['REMOTE_ADDR']
    else:
        ip = request.environ['HTTP_X_FORWARDED_FOR'] # if behind a proxy
    return ip

""" =================================== """
from slugify import slugify
def slugify(item_name):
    return slugify(item_name.lower())

""" =============================== """
"""  Calculate percentage in Python
To calculate a percentage in Python:

Use the division / operator to divide one number by another.
Multiply the quotient by 100 to get the percentage.
The result shows what percent the first number is of the second. """

def calc_percent(x, y):
    try:
        #pcnt = (x / y ) * 100
        pcnt = ((x / y ) * 100) if x is not None and y is not None and y != 0 else 0

        #return "{:.2f}%".format(pcnt)
        return "{:.2f}%".format(pcnt)
    except ZeroDivisionError:
        return 0


""" print(cal_percent(60, 0))  # 👉️ inf
print(cal_percent(60, 60))  # 👉️ 0.0
print(cal_percent(60, 120))  # 👉️ 50.0 """

