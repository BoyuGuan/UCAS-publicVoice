import os, datetime, jieba, pickle, wordcloud, imageio
from multiprocessing import Pool
from collections import Counter


def saveVariable(variable, fileName):
    f = open(fileName, 'wb')
    pickle.dump(variable, f)
    f.close()

def loadVariable(fileName):
    f = open(fileName, 'rb')
    variable = pickle.load(f)
    f.close()
    return variable

def handleDataPerMonth(month):
    """并行处理各月份的数据

    Args:
        month (int): 第几个月份的数据（对应第几个进程）
    """
    date = datetime.datetime.strptime(f'2023-{month}-01', '%Y-%m-%d')
    oneDay = datetime.timedelta(days = 1)
    allWordsCountInThisMonth = Counter()
    while date.month == month:
        MonthStrOfThisDate = str(date.month) if date.month >= 10 else '0' + str(date.month)
        dayStrOfThisDate = str(date.day) if date.day >= 10 else '0' + str(date.day)
        thisDateDataDir = './data/2023' + MonthStrOfThisDate + dayStrOfThisDate
        allFiles = os.listdir(thisDateDataDir)
        for fileName in allFiles:
            filePath = os.path.join(thisDateDataDir, fileName)
            with open(filePath, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    allWordsCountInThisMonth += Counter(jieba.lcut(line))

        date += oneDay
    return allWordsCountInThisMonth

def produceWordCount():
    p = Pool(5)
    results = p.map(handleDataPerMonth, [1, 2, 3, 4, 5])
    print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    print('\nAll subprocesses done.\n')

    allWordCount = Counter()
    for c in results:
        allWordCount += c
    saveVariable(allWordCount, './output/wordCounter.pickle')
    return allWordCount

def wordCloud( wordCount, savePath = './output/a.png'):
    mk = imageio.v3.imread("./star.png")
    stopWords = ['是','的','在','年','就','和', '了','对','为','让','从','好',
                 '将','也','日', '个', '不', '与', '地', '月', '下', '可', '来',
                 '到', '已', '这','都','并','们','各','向', '等', '说', '要', '有',
                 '日电', '但', '又', '日', '上', '时', '我', '会', '着', '他', '同',
                 '与', '由', '及', '被', '用', '把', '多','更', '而']
    w = wordcloud.WordCloud(width=1000,
                        height=700,
                        stopwords=stopWords,
                        background_color='white',
                        font_path='./font/msyh.ttf',
                        mask=mk,
                        collocations=False,
                        scale=15)
    words = ""
    for word, count in wordCount.items():
        if count > 10 :
            words += " " + " ".join([word,] * count)
    w.generate(words)
    w.to_file(savePath)




if __name__=='__main__':
    # allWordCount = produceWordCount()
    allWordCount = loadVariable('./output/wordCounter.pickle')
    wordCloud(allWordCount)
