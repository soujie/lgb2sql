from lgb2sql import node, Path


def dfs(tree):
    '''
    通过dfs +递归搜索单一树上的各条path
    当遍历到leaf 节点时, 将结果插入到path list 中
    当遍历到中间节点时, 继续让下
    '''
    def _dfs(node,res:Path):
        res.append(node)
        if node.is_leaf:
            path_list.append(str(res))
        else:
            if node.left_child:
                _dfs(node.left_child,res)
                res.pop()
            if node.right_child:
                res[-1].convert()
                _dfs(node.right_child,res)
                res.pop()
        
        
    path_list = list()
    path = Path()
    root = node(tree['tree_structure'])

    _dfs(root,path)
    print(path_list)





if __name__=='__main__':
    info = {'tree_index': 0,
   'num_leaves': 8,
   'num_cat': 0,
   'shrinkage': 1,
   'tree_structure': {'split_index': 0,
    'split_feature': 8,
    'split_gain': 756393,
    'threshold': 1.0000000180025095e-35,
    'decision_type': '<=',
    'default_left': True,
    'missing_type': 'None',
    'internal_value': 152.133,
    'internal_weight': 0,
    'internal_count': 442,
    'left_child': {'split_index': 2,
     'split_feature': 2,
     'split_gain': 167241,
     'threshold': 0.006188884713822097,
     'decision_type': '<=',
     'default_left': True,
     'missing_type': 'None',
     'internal_value': 148.162,
     'internal_weight': 230,
     'internal_count': 230,
     'left_child': {'split_index': 5,
      'split_feature': 6,
      'split_gain': 25738.900390625,
      'threshold': 0.021027815919496564,
      'decision_type': '<=',
      'default_left': True,
      'missing_type': 'None',
      'internal_value': 146.704,
      'internal_weight': 178,
      'internal_count': 178,
      'left_child': {'leaf_index': 0,
       'leaf_value': 147.8934691049083,
       'leaf_weight': 90,
       'leaf_count': 90},
      'right_child': {'leaf_index': 6,
       'leaf_value': 145.48831759066178,
       'leaf_weight': 88,
       'leaf_count': 88}},
     'right_child': {'split_index': 6,
      'split_feature': 3,
      'split_gain': 25425.30078125,
      'threshold': -0.016567045631320297,
      'decision_type': '<=',
      'default_left': True,
      'missing_type': 'None',
      'internal_value': 153.151,
      'internal_weight': 52,
      'internal_count': 52,
      'left_child': {'leaf_index': 3,
       'leaf_value': 150.66796185910738,
       'leaf_weight': 23,
       'leaf_count': 23},
      'right_child': {'leaf_index': 7,
       'leaf_value': 155.12013577175767,
       'leaf_weight': 29,
       'leaf_count': 29}}},
    'right_child': {'split_index': 1,
     'split_feature': 2,
     'split_gain': 215133,
     'threshold': 0.018044817526510912,
     'decision_type': '<=',
     'default_left': True,
     'missing_type': 'None',
     'internal_value': 156.442,
     'internal_weight': 212,
     'internal_count': 212,
     'left_child': {'split_index': 4,
      'split_feature': 2,
      'split_gain': 51547.69921875,
      'threshold': -0.021834229207078684,
      'decision_type': '<=',
      'default_left': True,
      'missing_type': 'None',
      'internal_value': 153.517,
      'internal_weight': 115,
      'internal_count': 115,
      'left_child': {'leaf_index': 1,
       'leaf_value': 150.56116141330108,
       'leaf_weight': 39,
       'leaf_count': 39},
      'right_child': {'leaf_index': 5,
       'leaf_value': 155.03329366770606,
       'leaf_weight': 76,
       'leaf_count': 76}},
     'right_child': {'split_index': 3,
      'split_feature': 2,
      'split_gain': 69583.296875,
      'threshold': 0.06870198499890849,
      'decision_type': '<=',
      'default_left': True,
      'missing_type': 'None',
      'internal_value': 159.911,
      'internal_weight': 97,
      'internal_count': 97,
      'left_child': {'leaf_index': 2,
       'leaf_value': 158.11864323619892,
       'leaf_weight': 67,
       'leaf_count': 67},
      'right_child': {'leaf_index': 4,
       'leaf_value': 163.9134691075574,
       'leaf_weight': 30,
       'leaf_count': 30}}}}}
    
    # vertex = node(info['tree_structure'])
    dfs(info)