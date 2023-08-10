import lightgbm as lgb 

class Node:
    def __init__(self,node_info:dict,depth = 0) -> None:
        self.is_leaf = self.check_is_leaf(node_info)
        self.depth = depth
        self.left_child = None
        self.right_child = None
        if not self.is_leaf:    
            self.node_id = node_info['split_index']
            self.feature = f"f_({str(node_info['split_feature'])})"
            self.thres = node_info['threshold']
            self.decision_type = 0 if node_info['decision_type'] == '<=' else 1  # 0 : <=  , 1:>
            self.left_child = Node(node_info['left_child'],depth+1) if 'left_child' in node_info.keys() else None 
            self.right_child = Node(node_info['right_child'],depth+1) if 'right_child' in node_info.keys() else None 
        
        else :
            self.leaf_value = node_info['leaf_value']
    
    def check_is_leaf(self,node_info:dict):
        return True if 'leaf_index' in node_info.keys() else False
    
    def __repr__(self) -> str:
        ans = '    '*self.depth
        if self.is_leaf:
            ans += f'{self.leaf_value}'
        else:
            if self.decision_type ==0:
                ans += f'CASE WHEN {self.feature} <= {self.thres} OR {self.feature } is null THEN'
                # ans += f'CASE WHEN {self.feature} <= {self.thres}' 
            else:
                ans += f'ELSE'
        return ans
            
    def __str__(self) -> str:
        return self.__repr__()
    
    def convert(self):
        self.decision_type = abs(1-self.decision_type)





class Path(list):
    def __init__(self):
        self.tree_strs = []
    
    def add(self,node:Node):
        self.append(node)
        self.tree_strs.append(str(node))
    
    def export(self):
        return '\n'.join(self.tree_strs)
    
    def convert(self):
        self[-1].convert()
        self.tree_strs.append(str(self[-1]))
    
    def end(self):
        tmp = '    '*(self[-1].depth-1)
        tmp += 'END'
        self.tree_strs.append(tmp)
        

        

class lgb2sql:
    def __init__(self,lgb_model:lgb.LGBMRegressor,) -> None:
        self.booster = lgb_model.booster_
        self.model_json = self.booster.dump_model()
        self.objective = self.model_json['objective']
        self.feature_names = self.model_json['feature_names']
        self.feature_mapper = dict(zip([f'f_({i})' for i in range(len(self.feature_names))],self.feature_names))
        self.trees = self.model_json['tree_info']
        
    def dfs(self,tree,id):
        def _dfs(node,res:Path):
            if not node.is_leaf:
                res.add(node)
                if node.left_child :
                    _dfs(node.left_child,res)
                    res.pop()
                if node.right_child :
                    res.convert()
                    _dfs(node.right_child,res)
                    res.end()
                    res.pop()
            else:
                res.add(node)
       
        path = Path()
        root = Node(tree['tree_structure'])

        _dfs(root,path)
        # tree_query = ',CASE \n'
        tree_query = ','
        tree_query += path.export()
        tree_query += f' AS subtree_{id} \n'
        return tree_query

    def export_sql(self,export_path:str,pk:str,feature_table:str = None):
        if self.objective == 'regression':
            obj_query = '\n ,'+'+'.join([f'subtree_{i}' for i in range(len(self.trees))])+' AS Score'
        elif self.objective == 'binary sigmoid:1':
            obj_query = f"\n ,1/EXP(1+(-({'+'.join([f'subtree_{i}' for i in range(self.trees)])})))"+' AS Score'
        else:
            raise ValueError()
        
        base_query =  f'SELECT \n {pk} {obj_query} \n FROM( \n'
        base_query += f'SELECT \n {pk} \n'
        
        total_tree_query = []
        for i,tree in enumerate(self.trees):
            total_tree_query.append(self.dfs(tree,i))
        
        tree_query = ''.join(total_tree_query)
        
        base_query+= tree_query
        
        if feature_table:
            base_query+= f'\n from {feature_table} \n )'  +'t'    
        else:
            base_query+= f'\n from 入模变量表 \n )' +'t'
        
        
        mapper = dict(sorted(self.feature_mapper.items(),key=lambda x:x[0],reverse=True))    
        for k,v in mapper.items():
            base_query=base_query.replace(k,v)
            
        if export_path:
            with open(export_path,'w',encoding='utf-8') as f :
                f.write(base_query)
        
        return base_query 