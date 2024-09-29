cate = Cate.query.order_by(Cate.id).all()

    length = [ { c.id } for c in cate if c.parent == None and c.lev == 0 ] #length of parent category
    
    #return f"{length}"
    #return f"{length}"

    """ for c in cate:
        if (c.parent == None and c.lev == 0):
            cat = [ {'id': c.id, 'parent': c.parent, 'name': c.name, 'lev':c.lev } for c in c ]
        elif (c.parent == 1 and c.lev == 1):
            cat = [ {'id': c.id, 'parent': c.parent, 'name': c.name, 'lev':c.lev } for c in c ]
        elif (c.parent == 2 and c.lev == 2):
            cat = [ {'id': c.id, 'parent': c.parent, 'name': c.name, 'lev':c.lev } for c in c ]
        elif (c.parent == 3 and c.lev == 3):
            cat = [ {'id': c.id, 'parent': c.parent, 'name': c.name, 'lev':c.lev } for c in c ] """

    """ elif (c.parent == 3 and c.lev == 3):
            cat = [ {'id': c.id, 'parent': c.parent, 'name': c.name, 'lev':c.lev } for c in c ] """

        #return cat

    _super = [ {c.name, c.id, c.parent, c.lev } for c in cate if c.parent == None and c.lev == 0 ] 
    _main = [ {c.name, c.id, c.parent, c.lev } for c in cate if c.parent == 1 and c.lev == 1 ]  
    _sub = [ {c.name, c.id, c.parent, c.lev } for c in cate if c.parent == 2 and c.lev == 2 ]  
    _mini = [ {c.name, c.id, c.parent, c.lev } for c in cate if c.parent == 3 and c.lev == 3 ]  

    """ _super = [ {c.name, c.id, c.parent, c.lev } for c in cate ] if cate.parent is None and cate.lev is 0 else None
    _main = [ {c.name, c.id, c.parent, c.lev } for c in cate ] if cate.parent is 1 and cate.lev is 1 else None
    _sub = [ {c.name, c.id, c.parent, c.lev } for c in cate ] if cate.parent is 2 and cate.lev is 2 else None
    _mini = [ {c.name, c.id, c.parent, c.lev } for c in cate ] if cate.parent is 3 and cate.lev is 3 else None
 """
    
    
    #cate_context = [{ _super ,  _main, _sub, _mini }]
    #return jsonify(cate_context)

    cate_context = {'super': _super , 'main': _main, 'sub': _sub, 'mini': _mini }

    #return f'{cate_context}'

    #context = {'item': items, 'cate': [{c.name, c.id, c.parent, c.lev } for c in cate] , 'cate':cate_context }
    

    cate = [ {'id': c.id, 'parent': c.parent, 'name': c.name, 'lev':c.lev } for c in cate ]

    #return jsonify(cate)

    def list_to_tree(data):
        out = {}
        for p in data:
            out.setdefault(p['parent'], {'children': []})
            out.setdefault(p['id'], {'children': []})
            out[ p['id']].update({'name': p['name']})
            out[p['parent']]['children'].append(out[p['id']])
        return out


    tree = list_to_tree(cate)

    #pprint.pprint(tree)

    #return f'{tree}'



    data = [

        { 'id': 1, 'parent': 2, 'name': "Node1" },
        { 'id': 2, 'parent': 5, 'name': "Node2" },
        { 'id': 3, 'parent': 0, 'name': "Node3" },
        { 'id': 5, 'parent': 0, 'name': "Node5" },
        { 'id': 9, 'parent': 1, 'name': "Node9" }
    ]

    
    def categ(cate):
        cat = {}
        for c in cate:
            cat.setdefault(c['parent'], { 'sub': [] })
            cat.setdefault(c['id'], { 'sub': [] })
            cat[c['id']].update(c)
            cat[c['parent']]['sub'].append(cat[c['id']])

        return cat
        #return f"{jsonify(cat)}"

    f = categ(data)
    pprint.pprint(f)
    return f'{f}'

    """ cat = {
                #'name': ''
                'super': { 
                        'name' : c['name'] or 'super-cate',
                        'main': {
                            'name': c['name'] or 'main-cate',
                            'sub': {
                                'name': 'sub-cate',
                                'mini' : {
                                    'mini-cate',
                                }

                            }
                        }
                    
                    },
                    } """
        
    """ for k in c:
        print(c['name'])
        #print(k, ':', c[k])
        print('\n') """
            
            
            #return f'{ k , c[k] }'

    context = {
        'cate': cate,

        'super':_super, 'main':_main, 'sub':_sub, 'mini':_mini
    }

    """     ids = [ i.id  for i in cate ] 
    parent = [ p.parent  for p in cate ] 
         return f"{ids, parent}"

       """
    """ data = []

    indexx = []

    id = [ i.id  for i in cate ]

    parent = [ p.parent  for p in cate ] or None """

    #data[int(id)] = [ { 'id': c.id, 'parent': c.parent, 'name': c.name, 'lev':c.lev } for c in cate ] 

    #return f" {(id), (parent)}"

    #return jsonify([ { 'id': c.id, 'parent': c.parent, 'name': c.name, 'lev':c.lev } for c in cate ] ) 
    
    #return jsonify([ { 'label': c.title, 'url': url_for('main.prev', slug=c.slug) } for c in c] ) 