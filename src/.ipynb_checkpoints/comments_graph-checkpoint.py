#!/usr/bin/python

import pandas as pd
import os
import sys
import numpy as np
import vaex
import string
import re
from textblob import TextBlob
import nltk
from nltk.corpus import stopwords
from nltk import word_tokenize
nltk.download('stopwords')
import datashader as ds
import holoviews as hv
from holoviews import opts
from holoviews.operation.datashader import datashade, shade, dynspread, spread, rasterize
from holoviews.operation import decimate
import holoviews.operation.datashader as hd
from holoviews.operation import histogram
from bokeh.models import HoverTool
hd.shade.cmap=["lightblue", "darkblue"]
hv.extension('bokeh')
import scattertext as st

# TODO: additional buttons, better tooltips for both

# function for cleaning text comments
def clean_comments(comment):
    # tokenize, remove punctuation and capitalization
    comment = comment.split(' ')
    comment = [c.lower() for c in comment]
    comment = [re.sub(r'[^\w\s]', '', c) for c in comment]
    comment = [c for c in comment if c not in vc.vocab.stop.words]
    comment = ' '.join(comment)
    return comment

# misinformation finder modified 
def misinfo_finder(post, links):
    # checks url and url_overridden_by_dest against links to see if any urls 
    # are in the list of untrustworthy domains
    url = post['url']
    full_link = post['full_link']
    over_url = post['url_overridden_by_dest']
    info = 'true_info'
    for link in links:
        if link in over_url:
            info = 'misinfo'
            url = over_url
            break
        if link in url:
            info = 'misinfo'
            break
    post['misinfo'] = info
    post['url'] = url
    post = post[['subreddit', 'full_link', 'author', 'misinfo']]
    return post


def make_plots():
    sublist = ['alltheleft', 'AmericanPolitics', 'Anarchism', 'Anarchist', 'AnarchoPacifism', 
                'blackflag',  'Capitalism', 'Communist', 'Conservative', 'conservatives', 
                'conspiracy', 'democracy','democrats', 'GreenParty', 'Liberal', 'Libertarian',
                'LibertarianSocialism', 'Liberty', 'moderatepolitics', 'neoprogs', 'politics', 
                'progressive','republicanism', 'Republican', 'republicans', 'SocialDemocracy',
                'socialism', 'uspolitics']

    # save links, move to data dir
    with open('misinfo_sites.txt') as file:
        links = [link.strip() for link in file]
    os.chdir('..')
    os.chdir('..')
    cur_dir = os.getcwd()
    os.chdir(cur_dir + '/data')

    # grab data, convert to vaex
    jsonl_list = [sub + '_posts.jsonl' for sub in sublist]
    csv_list = [sub + '_comments.csv' for sub in sublist]
    csv_list_hdf5 = [sub + '_comments.csv.hdf5' for sub in sublist]

    for csv in csv_list:
        comment_files = vaex.from_csv(csv, convert=True, copy_index=False)
    comments = vaex.open_many(csv_list_hdf5)

    posts = vaex.from_json(jsonl_list[0], orient='records', lines=True, copy_index=False)
    for jsonl in jsonl_list[1:]:
        posts = posts.concat(vaex.from_json(jsonl, orient='records', lines=True, copy_index=False))

    # get comments, combine, merge with posts on full_link
    comments['comment'] = comments.comment.apply(clean_comments)

    temp = posts.to_pandas_df(column_names=['subreddit', 'full_link', 'url', 'url_overridden_by_dest', 'author'])
    temp = temp.apply(misinfo_finder, links=links, axis=1)
    posts = vaex.from_pandas(temp)
    df = posts.join(comments, how='right', on='full_link')

    # sentiment polarity (1 = positive, -1 = negative)
    # sentiment subjectivity (1 = subjective, 0 = objective)
    df['polarity'] = df.comment.apply(lambda x: TextBlob(x).sentiment.polarity)
    df['subjectivity'] = df.comment.apply(lambda x: TextBlob(x).sentiment.subjectivity)

    comments_0 = df[df.misinfo == 'true_info']
    comments_1 = df[df.misinfo == 'misinfo']

    # first plot: polarity and subjectivity by type of information
    points_0 = hv.Points(comments_0.to_pandas_df(), 
                         kdims=['polarity', 'subjectivity'], 
                         vdims=['subreddit', 'misinfo'], 
                         label="True Information").opts(colorbar=True, 
                                                        tools=["hover"], 
                                                        width=750, 
                                                        height=750, 
                                                        alpha=.4, 
                                                        title = 'Sentiment Polarity vs. Subjectivity by Information Type', 
                                                        xlabel = 'Polarity', 
                                                        ylabel = 'Subjectivity')

    points_1 = hv.Points(comments_1.to_pandas_df(), 
                         kdims=['polarity', 'subjectivity'], 
                         vdims=['subreddit', 'misinfo'], 
                         label="Misinformation").opts(colorbar=True, 
                                                        tools=["hover"], 
                                                        width=750, 
                                                        height=750, 
                                                        alpha=.7, 
                                                        title = 'Sentiment Polarity vs. Subjectivity by Information Type', 
                                                        xlabel = 'Polarity', 
                                                        ylabel = 'Subjectivity')

    xhist, yhist = (histogram(points_0, dimension=dim, normed=True) *
                    histogram(points_1, dimension=dim, normed=True) 
                    for dim in ['polarity', 'subjectivity'])

    plot = (points_0 * points_1) << yhist << xhist
    plot.opts(opts.Histogram(alpha=0.3))

    # move to src, save interactive graph
    os.chdir('..')
    cur_dir = os.getcwd()
    os.chdir(cur_dir + 'DSC180B_Group5/src')
    hv.save(plot, 'comments_graph_1.html')

    # second plot: scatter text
    # create corpus
    nlp = st.WhitespaceNLP.whitespace_nlp
    corpus = st.CorpusFromPandas(df.to_pandas_df(), 
                                 category_col='misinfo', 
                                 text_col='comment', 
                                 nlp=nlp).build()

    # grab stats and save in csv file
    # misinfo = False
    term_freq_df = corpus.get_term_freq_df()
    term_freq_df['true_info'] = corpus.get_scaled_f_scores('true_info')
    top_15_true = term_freq_df.true_info.sort_values(ascending=False).index[:15]

    # misinfo = True
    term_freq_df['misinfo'] = corpus.get_scaled_f_scores('misinfo')
    top_15_mis = term_freq_df.misinfo.sort_values(ascending=False).index[:15]

    out = pd.DataFrame({'True Information': top_15_true, 'Misinformation': top_15_mis})
    # out = out.style.set_caption("Top 15 Associated Words/Phrases")
    out.to_csv('comments_misinfo_words.csv', index=False)

    # create plot, save
    # later: subreddits in tooltips, search bar

    html = st.produce_scattertext_explorer(corpus, 
                                           category='misinfo', 
                                           category_name='misinfo', 
                                           not_category_name='true_info', 
                                           width_in_pixels=1000, 
                                           metadata=corpus.get_df()['subreddit'])

    open("comments_graph_2.html", 'wb').write(html.encode('utf-8'))
    
    
def make_plots_test():
    # save links, move to test/testdata dir
    with open('misinfo_sites.txt') as file:
        links = [link.strip() for link in file]
    os.chdir('..')
    cur_dir = os.getcwd()
    os.chdir(cur_dir + '/test/testdata')

    # grab data, convert to vaex
    jsonl = 'test.jsonl'
    csv = 'test_comments.csv'
    csv_hdf5 = 'test_comments.csv.hdf5'

    comment_file = vaex.from_csv(csv, convert=True, copy_index=False)
    comments = vaex.open(csv_hdf5)
    posts = vaex.from_json(jsonl, orient='records', lines=True, copy_index=False)

    # get comments, combine, merge with posts on full_link
    comments['comment'] = comments.comment.apply(clean_comments)

    temp = posts.to_pandas_df(column_names=['subreddit', 'full_link', 'url', 'url_overridden_by_dest', 'author'])
    temp = temp.apply(misinfo_finder, links=links, axis=1)
    posts = vaex.from_pandas(temp)
    df = posts.join(comments, how='right', on='full_link')

    # sentiment polarity (1 = positive, -1 = negative)
    # sentiment subjectivity (1 = subjective, 0 = objective)
    df['polarity'] = df.comment.apply(lambda x: TextBlob(x).sentiment.polarity)
    df['subjectivity'] = df.comment.apply(lambda x: TextBlob(x).sentiment.subjectivity)

    comments_0 = df[df.misinfo == 'true_info']
    comments_1 = df[df.misinfo == 'misinfo']

    # first plot: polarity and subjectivity by type of information
    points_0 = hv.Points(comments_0.to_pandas_df(), 
                         kdims=['polarity', 'subjectivity'], 
                         vdims=['subreddit', 'misinfo'], 
                         label="True Information").opts(colorbar=True, 
                                                        tools=["hover"], 
                                                        width=750, 
                                                        height=750, 
                                                        alpha=.4, 
                                                        title = 'Sentiment Polarity vs. Subjectivity by Information Type', 
                                                        xlabel = 'Polarity', 
                                                        ylabel = 'Subjectivity')

    points_1 = hv.Points(comments_1.to_pandas_df(), 
                         kdims=['polarity', 'subjectivity'], 
                         vdims=['subreddit', 'misinfo'], 
                         label="Misinformation").opts(colorbar=True, 
                                                        tools=["hover"], 
                                                        width=750, 
                                                        height=750, 
                                                        alpha=.7, 
                                                        title = 'Sentiment Polarity vs. Subjectivity by Information Type', 
                                                        xlabel = 'Polarity', 
                                                        ylabel = 'Subjectivity')

    xhist, yhist = (histogram(points_0, dimension=dim, normed=True) *
                    histogram(points_1, dimension=dim, normed=True) 
                    for dim in ['polarity', 'subjectivity'])

    plot = (points_0 * points_1) << yhist << xhist
    plot.opts(opts.Histogram(alpha=0.3))

    # save interactive graph
    hv.save(plot, 'test_comments_graph_1.html')

    # second plot: scatter text
    # create corpus
    nlp = st.WhitespaceNLP.whitespace_nlp
    corpus = st.CorpusFromPandas(df.to_pandas_df(), 
                                 category_col='misinfo', 
                                 text_col='comment', 
                                 nlp=nlp).build()

    # grab stats and save in csv file
    # misinfo = False
    term_freq_df = corpus.get_term_freq_df()
    term_freq_df['true_info'] = corpus.get_scaled_f_scores('true_info')
    top_10_true = term_freq_df.true_info.sort_values(ascending=False).index[:10]

    # misinfo = True
    term_freq_df['misinfo'] = corpus.get_scaled_f_scores('misinfo')
    top_10_mis = term_freq_df.misinfo.sort_values(ascending=False).index[:10]

    out = pd.DataFrame({'True Information': top_10_true, 'Misinformation': top_10_mis})
    # out = out.style.set_caption("Top 10 Associated Words/Phrases")
    out.to_csv('test_comments_misinfo_words.csv', index=False)

    # create plot, save
    html = st.produce_scattertext_explorer(corpus, 
                                           category='misinfo', 
                                           category_name='misinfo', 
                                           not_category_name='true_info', 
                                           width_in_pixels=1000, 
                                           metadata=corpus.get_df()['subreddit'])
    
    # later: subreddits in tooltips, search bar

    open("test_comments_graph_2.html", 'wb').write(html.encode('utf-8'))
    

    # third plot with flag words from vocab class? histogram?


def main(targets):
    if targets == 'test':
        make_plots_test()
    else:
        make_plots()

if __name__ == '__main__':
    targets = sys.argv[1]
    main(targets)

########### Unused CountVectorizer + MultinomialNB Pipeline

# from sklearn.linear_model import LogisticRegression
# from sklearn.model_selection import train_test_split, GridSearchCV
# from sklearn.pipeline import Pipeline
# from sklearn.naive_bayes import MultinomialNB
# from sklearn import metrics
# from sklearn.metrics import accuracy_score, recall_score, precision_score, confusion_matrix
# from sklearn.feature_extraction import text
# from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
# X_train = df['comment']
# y_train = df['misinfo']

# pipe = Pipeline([('cvec', CountVectorizer()),    
#                  ('nb', MultinomialNB())])

# pipe_params = {'cvec__ngram_range': [(1,1),(1,3)],
#                'nb__alpha': [.36, .6]}

# gs = GridSearchCV(pipe, param_grid=pipe_params, cv=3)
# gs.fit(X_train, y_train)

# print("Best score:", gs.best_score_)
# print("Train score", gs.score(X_train, y_train))
# # print("Test score", gs.score(X_test, y_test))

# # for test set 
# # instantiate classifier and vectorizer
# nb = MultinomialNB(alpha = 0.36)
# cvec = CountVectorizer(ngram_range= (1, 3))

# cvec.fit(X_train)

# Xcvec_train = cvec.transform(X_train)
# # Xcvec_test = cvec.transform(X_test)

# nb.fit(Xcvec_train, y_train)
# # preds = nb.predict(Xcvec_test)

# # print(nb.score(Xcvec_test, y_test))