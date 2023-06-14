import os, datetime
import matplotlib.pyplot as plt
from collections import Counter
from multiprocessing import Pool
import jieba

TARGETWORDS = ['十四届全国人大', '十四届全国人民代表大会', '两会', '全国政协十四届',
                '政协第十四届']

def wordAnalysisPerMonth(month):
    """并行处理各月份的数据

    Args:
        month (int): 第几个月份的数据（对应第几个进程）
    """
    date = datetime.datetime.strptime(f'2023-{month}-01', '%Y-%m-%d')
    oneDay = datetime.timedelta(days = 1)
    allWordsCountAboutTargetInThisMonth = Counter()

    while date.month == month:
        MonthStrOfThisDate = str(date.month) if date.month >= 10 else '0' + str(date.month)
        dayStrOfThisDate = str(date.day) if date.day >= 10 else '0' + str(date.day)
        thisDateDataDir = './data/2023' + MonthStrOfThisDate + dayStrOfThisDate
        allFilesInThisDate = os.listdir(thisDateDataDir)
        for fileName in allFilesInThisDate:
            filePath = os.path.join(thisDateDataDir, fileName)
            with open(filePath, encoding="utf-8") as f:
                context = f.readlines()
                context = "".join(context)
                for targetWord in TARGETWORDS:
                    if targetWord in context:
                        allWordsCountAboutTargetInThisMonth += Counter(jieba.lcut(context))
                        break
        date += oneDay

    return allWordsCountAboutTargetInThisMonth

def produceWordCount():
    p = Pool(5)
    results = p.map(wordAnalysisPerMonth, [1, 2, 3, 4, 5])
    print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    print('\nAll subprocesses done.\n')

    allWordsRelated = Counter()
    for wordsRelated in results:
        allWordsRelated += wordsRelated

    return allWordsRelated




if __name__=='__main__':
    print(produceWordCount())