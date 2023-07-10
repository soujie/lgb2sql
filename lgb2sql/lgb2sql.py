import lightgbm as lgb 

class node:
    def __init__(self,node_info:dict) -> None:
        self.is_leaf = self.check_is_leaf(node_info)
        if not self.is_leaf:    
            self.node_id = node_info['split_index']
            self.feature = 'f_'+str(node_info['split_feature'])
            self.thres = node_info['threshold']
            self.decision_type = 0 if node_info['decision_type'] == '<=' else 1  # 0 : <=  , 1:>
            self.left_child = node(node_info['left_child']) if 'left_child' in node_info.keys() else None 
            self.right_child = node(node_info['right_child']) if 'right_child' in node_info.keys() else None 
        
        else :
            self.leaf_value = node_info['leaf_value']
    
    def check_is_leaf(self,node_info:dict):
        return True if 'leaf_index' in node_info.keys() else False
    
    def __repr__(self) -> str:
        ans = ''
        if self.is_leaf:
            ans += f'{self.leaf_value}'
        else :
            decision = '<=' if self.decision_type == 0 else '>'
            ans += f'{self.feature} {decision} {self.thres}'
        return ans 
    
    def __str__(self) -> str:
        return self.__repr__()
    
    def convert(self):
        self.decision_type = abs(1-self.decision_type)
        

class Path(list):
    def __repr__(self) -> str:
        ans = 'WHEN '
        ans += str(self[0])+' \n '
        if len(self)>1:
            for i in range(1,len(self)):
                if self[i].is_leaf:
                    ans += 'THEN  ' + str(self[i])+' \n '
                else:
                    ans += f' AND {str(self[i])} \n'
        return ans
    
    def __str__(self) -> str:
        return self.__repr__()

class lgb2sql:
    def __init__(self,lgb_model:lgb.LGBMRegressor,) -> None:
        self.booster = lgb_model.booster_
        self.model_json = self.booster.dump_model()
        self.objective = self.model_json['objective']
        self.feature_names = self.model_json['feature_names']
        self.feature_mapper = dict(zip([f'f_{i}' for i in range(len(self.feature_names))],self.feature_names))
        self.trees = self.model_json['tree_info']
        
    def dfs(self,tree,id):
        '''
        通过dfs +递归搜索单一树上的各条path
        当遍历到leaf 节点时, 将结果插入到path list 中
        当遍历到中间节点时, 继续
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
        tree_query = ',CASE \n'
        tree_query += ''.join(path_list)
        tree_query += f'END AS subtree_{id} \n'
        return tree_query

    def export_sql(self,export_path:str,pk:str,feature_table:str = None):
        if self.objective == 'regression':
            obj_query = '\n ,'+'+'.join([f'subtree_{i}' for i in range(len(self.trees))])+' AS Score'
        elif self.objective == 'binary sigmoid:1':
            obj_query = f"\n ,1/EXP(-({'+'.join([f'subtree_{i}' for i in range(self.trees)])}))"+' AS Score'
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