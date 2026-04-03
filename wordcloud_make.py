from wordcloud import WordCloud,STOPWORDS
import matplotlib.pyplot as plt

text=open(r'C:\Users\agrow\OneDrive\Desktop\새 폴더 (2)\alice.txt',encoding='utf-8').read()
wordcloud = WordCloud(max_words=100,stopwords=STOPWORDS).generate(text)

plt.figure(figsize=(15,10))
plt.imshow(wordcloud)

plt.axis('off')
plt.show()