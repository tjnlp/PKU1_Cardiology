# coding: utf - 8
import re
import xlrd
import xlwt
import linecache
from KDEngine import ExtractData
def new_judge_rules(line):
	p1 = u'(无|谨防|未|警惕|注意|除外|如有).*血肿'
	p2 = u'((硬膜|蛛网膜)(下|外).{0,3}血肿)|额部血肿'
	p3 = u'(血肿.*(不除外|不能完全除外))|((继续|是否存在|不除外|不能完全除外).*血肿)|血肿大小|血肿变大可能|血肿范围是否扩大'
	p4 = u'(血肿.*(未触及|可能性(小|不大)|除外))|血肿瘤'
	p5 = u'((防止|形成|以防).*血肿.*(发生|风险|形成))|充血肿胀'
	if re.search(p3, line):
		return str(1)
	elif u'血肿' not in line or re.search(p1, line) or re.search(p2, line)  or re.search(p4,line) or re.search(p5,line):
		return str(0)
	else:
		return str(1)
def new_judge_rules_ex(line):
	p1 = u'(无|谨防|未|警惕|注意|除外|如有).*血肿'
	p2 = u'((硬膜|蛛网膜)(下|外).{0,3}血肿)|额部血肿'
	p3 = u'(血肿.*(不除外|不能完全除外))|((继续|是否存在|不除外|不能完全除外).*血肿)|血肿大小|血肿变大可能|血肿范围是否扩大'
	p4 = u'(血肿.*(未触及|可能性(小|不大)|除外))|血肿瘤'
	p5 = u'((防止|形成|以防).*血肿.*(发生|风险|形成))|充血肿胀'
	if re.search(p3, line):
		return 25, str(1)
	elif u'血肿' not in line or re.search(p1, line) or re.search(p2, line)  or re.search(p4,line) or re.search(p5,line):
		return 27, str(0)
	else:
		return 29, str(1)


# 根据上面的pattern判断的各个语句的结果，来确定该病人是否患有血肿,但凡有一个语句判断为1，我们便认为病人患有血肿
def is_patient_hematoma(judge_result):
	if judge_result.count('1') > 0:
		return 1
	else:
		return 0

# 将1份病例先按“，”、“。”、“；”、“！”、“？”分句后，提取含有血肿的字段，获得句子scope
def emr_divide(text):
	divide_list = []
	for i in [u'，', u'。', u'；',u'？',u'！']:
		text = text.replace(i, '@')
	text_list = text.split('@')
	for i in text_list:
		if u'血肿' in i:
			divide_list.append(i)
	return divide_list

# 1、如果我们的训练文档是excel文件：
# 将text文档中的所有病历读入一个字典，keys是病历号，values是病历内容
def read_excel(file):
	data = xlrd.open_workbook(file)
	table = data.sheet_by_index(0)        # 获得第一张sheet
	nrow = table.nrows        # 行数
	texts = {i: table.cell(i, 2).value for i in range(1, nrow)}
	return texts        # texts中的value都是unicode

# read_excel('20161014_hematoma_eval.xlsx')

# 将结果写入文件result_file中，判断规则为judge_pattern
def write_excel(file, result_file, emr_divide = emr_divide, judge_pattern = new_judge_rules):
	# 建立一个新的excel文件，命名一个sheet为result来储存结果
	data = xlwt.Workbook()
	sheet1 = data.add_sheet('result', cell_overwrite_ok = True)
	row1 = [u'原始行号', u'句段scope', u'是否血肿_scope', u'是否血肿_patient']
	# print type(row1[1])
	for i in range(len(row1)):
		sheet1.write(0, i, row1[i])
	texts = read_excel(file)
	m = 1
	for i in texts.keys():
		divide_text = emr_divide(texts[i])
		n = len(divide_text)
		patient_result = []
		for j in range(n):
			patient_result.append(judge_pattern(divide_text[j]))
			sheet1.write(m+j, 1, divide_text[j])
			sheet1.write(m+j, 2, judge_pattern(divide_text[j]))
		sheet1.write(m, 0, i)
		sheet1.write(m+n, 0, i)
		sheet1.write(m+n, 3, is_patient_hematoma(patient_result))
		m = m + n + 1
	data.save(result_file)

#2、如果我们的训练文档是txt文档：
def read_txt(file):
	inf = open(file,"r")
	linecount = len(inf.readlines())
	texts = {i: linecache.getline(file, i).strip().decode('utf-8') for i in range(1, linecount + 1)}
	inf.close()
	return texts
# print read_txt('20161014_hematoma_eval.txt')

def write_txt(file,result_file,emr_divide = emr_divide, judge_pattern = new_judge_rules):
	outf = open(result_file,"w") 
	firstline = '原始行号'+"\t"+'是否血肿_patient'+"\t"+'句段scope'+"\t"+'是否血肿_scope'+"\n"
	outf.write(firstline)
	text = read_txt(file)		
	for i in text.keys():
		divide_text = emr_divide(text[i])
		n = len(divide_text)
		patient_result = []
		for j in range(n):
			patient_result.append(judge_pattern(divide_text[j]))
			outf.write(str(i)+"\t"*2+ divide_text[j].encode('utf-8')+"\t"+str(judge_pattern(divide_text[j]))+"\n")	
		outf.write(str(i)+"\t"+str(is_patient_hematoma(patient_result))+"\n")
	outf.close()
	
def splitSentence(sentence):
	number = sentence.count(u'血')
	indexList = [0]
	for i in range(number):
		print i
		begin = indexList[i]
		index = sentence.find(u'血', begin)
		indexList.append(index + 1)
	sentence_list = []
	fout = open('log.txt', 'w')
	for i in range(number):
		begin = indexList[i]
		if (i +2 ) >number:
			end = len(sentence)
		else:
			end = indexList[i + 2] -1
		segment = sentence[begin:end]
		sentence_list.append(segment)
		fout.write(segment.encode('utf8'))
		fout.write('\n')
	fout.close()
	return sentence_list
def test():
	target=u'血肿'
	
	import yaml
	yaml_path='mock.yaml'
	f=open(yaml_path)
	knol=yaml.load(f)
	f.close()

	knowledge={target:knol[target]}

	sentence=u'包扎，可见3cm*5cm血肿，上覆冰袋，血肿处无明显压痛及血管搏动，近心端纱布卷加'
	sentence=u'止血夹，局部伤口出血，且可见一2*8cm血肿，予局部压迫约10分钟，血肿较前减少，'
	segments = splitSentence(sentence)
	
	results = []
	fout = open('log.txt', 'a')
	for segment in segments:
		if int(new_judge_rules(segment)):
			fout.write(segment.encode('utf8'))
			fout.write('\t')
			ed=ExtractData(segment,knowledge)
			for rlt in ed.res:
				print rlt['value']
			fout.write('\n')




if __name__ == '__main__':
	# write_excel('20161014_hematoma_eval.xlsx', 'result.xlsx')
	# write_txt('20161014_hematoma_eval.txt', 'result.txt')
	test()
	print "finished"
