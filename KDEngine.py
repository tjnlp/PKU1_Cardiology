#coding:utf-8
###
#
#KDEngine: A Knowledge-Dependent Engine for Multiple Heart Disease Risk Factors Extraction
#paper: 
#version: 2016/01/04
###
import re
import copy
import types
from extendKeyword import dealWithKeyWord

class ExtractData():
    def __init__(self,sentence,knowledge):
        self.rawSen=sentence
        self.knol=knowledge
        self.itemName=self.knol.keys()[0]
        self.indicators=self.knol[self.itemName].keys()
        
        self.res=self.dataExtract(self.rawSen)
    
    def dataExtract(self,sen):
        #Binyang
        results=[]
        for indicator in self.indicators:
            #skip custom_form_code, deal with indicators only. @20160107 Yahui
            if indicator == 'key_code':
                continue
            
            knol=self.knol[self.itemName][indicator]
            #print 27, knol
            old_keywords=knol['keywords']
            negation=knol['negation']
            scope=knol['scope']
            value_type=knol['value_type']
            value_expression=knol['value_expression']
            value_unit=knol['value_unit']
            
            #20160107 extend keywords to improve CLIPS
            keywords = dealWithKeyWord(old_keywords)
            
            for kw in keywords: #每个kw都是一个元组,由1个或多个词组成
                kw_index=self.findKeywordIndex(sen,kw)
                kw_present=self.if_keyWords_coOccured(kw_index,len(kw[0]),scope)
                if kw_present==[]:  #若keyword组合不在该句中 (或不在scope指定范围内)
                    continue
                #result={'name':'', 'indicator':'','keyword':kw,'scope':[],'negation':False}
                result=self.detectNegation(sen,kw_present,kw,scope,negation)
                if result['negation']==False:
                    if value_type:
                        result=self.extract_values(result,value_expression)
                        result=self.extract_units(result,value_unit)
                    else:
                        result['value']=None
                        result['unit']=None
                    result['name'] = self.itemName
                    result['indicator'] = indicator
                    results.append(result)

        return results
                
    def detectNegation(self,sen,target_indexs,kw,scope,negation):
        #判断是否存在negation, Binyang
        pos_scopes=[]
        neg_scopes=[]
        neg_flag=0
        result={'name':'', 'indicator':'','keyword':kw,'scope':[],'negation':False}
        
        if scope!=[]:
            scope_len_f=scope[0]
            scope_len_b=scope[1]
        else:
            scope_len_f=999
            scope_len_b=999
        
        for index in target_indexs:
            start=max(0,index-scope_len_f)
            end=min(len(sen),index+len(kw[0])+scope_len_b)
            scope_text=sen[start:end]
            scope_marked=scope_text.replace(kw[0],'#######')    #以防keyword中自带一些否定词
            
            flag=0
            for nw in negation:
                if nw in scope_marked:
                    flag=1
            if flag:
                neg_flag=1
                neg_scopes.append(scope_text)
            else:
                pos_scopes.append(scope_text)
        
        if neg_flag:
            result['scope']=neg_scopes
            result['negation']=True
        else:
            result['scope']=pos_scopes
            result['negation']=False
        return result
                
    def extract_values(self, objects, value_expressions):
        #Yahui
        new_objects = copy.deepcopy(objects)
        new_objects['value'] = []
        if not objects.has_key('scope'):
            print '[Error] no scope for value extraction!'
            return None
        for s in objects['scope']:
            value_of_cur_scope = []
            for v_expr in value_expressions:
                v_pattern = re.compile(v_expr)
                for m in v_pattern.findall(s):
                    value_of_cur_scope += re.compile('\d+\.?\d*').findall(m)
            new_objects['value'].append(copy.deepcopy(value_of_cur_scope))
        return new_objects
    
    def extract_units(self, object, value_unit, addBoundry=True):
        #Binyang
        new_object=copy.deepcopy(object)
        new_object['unit'] = []
        if not object.has_key('scope'):
            print '[Error] no scope for value extraction!'
            return None
        for s in object['scope']:
            unit_of_cur_scope=[]
            for unit in value_unit:
                if addBoundry:
                    pa=re.compile('[\W\d]('+unit.replace('.','\.')+')\W')
                else:
                    pa=re.compile(unit.replace('.','\.'))
                ma=pa.findall(s)
                # print ma
                unit_of_cur_scope+=ma
            new_object['unit'].append(unit_of_cur_scope)
            
        return new_object
    
    def findKeywordIndex(self,sen,kw,addBoundry=False):
        #找到一组keywords中,每个词的index, Binyang
        all_indexs=[]
        if type(kw) is types.TupleType:
            for word in kw:
                one_index=[]
                if addBoundry:
                    pa=re.compile('[\W\d]'+word.replace('.','\.')+'\W')
                else:
                    pa=re.compile(word.replace('.','\.'))
                ma=pa.finditer(sen)
                for m in ma:
                    index=m.start()
                    one_index.append(index)
                all_indexs.append(one_index)
        else:
            'Keywords are not organized in tuple. Please check!!!'
        return all_indexs
        
    def if_keyWords_coOccured(self, kwpos = [[0,1], [2], [3,4]], pri_kw_len = 5, defied_scopes = [999, 999]):
        ###返回在scope范围内所有keywords均共现的所有第一关键字的index, Yahui
        #20151229 handle the empty kwpos
        if not len(kwpos):
            return []
        pos_pri_kws = []
        for index_pri_kw in kwpos[0]:
            scope_pri_kw = [index_pri_kw - defied_scopes[0], index_pri_kw + defied_scopes[1] + pri_kw_len]
            failed = 0
            coOccur_kws = kwpos[1:]
            for coOccur_kw in coOccur_kws:
                flag = 0
                for p in coOccur_kw:
                    if p >= scope_pri_kw[0] and p <= scope_pri_kw[1]:
                        flag = 1
                if flag == 0:   #当前关键字均不在第一关键字的scope内
                    failed = 1
                    break
            if failed:
                continue
            else:
                pos_pri_kws.append(index_pri_kw)
        return list(set(pos_pri_kws))

def test():
    import yaml
    yaml_path='fake.yaml'
    f=open(yaml_path)
    knol=yaml.load(f)
    f.close()
    
    sentence=u'冠脉造影呈右冠优势型150mm哈AAAAAAAAAAAAAAAAAAAAAA冠脉造影'
    target=u'冠脉造影'
    knowledge={target:knol[target]}
    ed=ExtractData(sentence,knowledge)
    for i in ed.res:
        print i

if __name__=='__main__':
    test()