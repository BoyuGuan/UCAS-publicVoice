import os, datetime
from collections import Counter
from multiprocessing import Pool
import jieba

from wordCloud import saveVariable, loadVariable

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
                for line in f:
                    for targetWord in TARGETWORDS:
                        if targetWord in line:
                            allWordsCountAboutTargetInThisMonth += Counter(jieba.lcut(line))
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

    allWordsRelatedCount = Counter()
    for wordsRelated in results:
        allWordsRelatedCount += wordsRelated
    return allWordsRelatedCount

def findMostRelativeWords():
    try:
        allRelativeWords = loadVariable('./output/realtiveWords.pickle')
    except:
        allRelativeWords = produceWordCount()
        saveVariable(allRelativeWords, './output/realtiveWords.pickle')
    allRelativeWords = list(allRelativeWords.items())
    allRelativeWords.sort(key = lambda x: x[1], reverse= True)
    for i in range(25):
        print(allRelativeWords[i*4], allRelativeWords[i*4 + 1], allRelativeWords[i*4 + 2], allRelativeWords[i*4 + 3])




if __name__ == '__main__':
    findMostRelativeWords()