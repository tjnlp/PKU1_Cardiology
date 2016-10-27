# coding: utf - 8
import re
import xlrd
import xlwt

# 这是新规则
def new_judge_rules(line):
	p1 = u'(无|谨防|未|警惕|注意|除外|如有).*血肿'
	p2 = u'((硬膜|蛛网膜)(下|外).{0,3}血肿)|额部血肿'
	p3 = u'(血肿.*(不除外|不能完全除外))|((继续|是否存在|不除外|不能完全除外).*血肿)|血肿大小|血肿变大可能|血肿范围是否扩大'
	p4 = u'(血肿.*(未触及|可能性(小|不大)|除外))|血肿瘤'
	# p5 = u'(防止.*血肿.*发生)|(形成.*血肿.*风险)|(以防.*血肿.*形成)|充血肿胀'
	p5 = u'((防止|形成|以防).*血肿.*(发生|风险|形成))|充血肿胀'
	if re.search(p3, line):
		return str(1)
	elif u'血肿' not in line or re.search(p1, line) or re.search(p2, line)  or re.search(p4,line) or re.search(p5,line):
		return str(0)
	else:
		return str(1)

# 根据上面的pattern判断的各个语句的结果，来确定该病人是否患有血肿,但凡有一个语句判断为1，我们便病人认为患有血肿
def is_patient_hematoma(judge_result):
	if judge_result.count('1') > 0:
		return 1
	else:
		return 0

# 将1份病例先按“，”、“。”、“；”、“！”、“？”、“,”分句后，提取含有血肿的字段，获得句子scope
def emr_divide(text):
	divide_list = []
	for i in [u'，', u'。', u'；',u'？',u'！',u',']:
		text = text.replace(i, '@')
	text_list = text.split('@')
	for i in text_list:
		if u'血肿' in i:
			divide_list.append(i)
	return divide_list


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

if __name__ == '__main__':
	write_excel('20161014_hematoma_eval.xlsx', 'result.xlsx', emr_divide, new_judge_rules)
	print "finished"

