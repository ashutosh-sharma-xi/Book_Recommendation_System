from flask import Flask, render_template, request
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import pickle
# getpredictions dataframe and books dataframe
pred_df = pickle.load(open('pred_df.pkl', 'rb'))
books = pickle.load(open('unique_books.pkl', 'rb'))
top_50_df = pickle.load(open('top_50_books.pkl', 'rb'))


def recommend_items_by_item(book_name, predictions_df, items_df=None, topn=10, verbose=False):

    pdt = predictions_df.transpose()
    cosine_similarities = cosine_similarity(
        np.array(pdt[book_name]).reshape(1, -1), predictions_df)
    recommended_df = pd.DataFrame({'recStrength': cosine_similarities[0]}, index=predictions_df.index).sort_values(
        by='recStrength', ascending=False)
    recommended_df = recommended_df.iloc[:topn,]
    # print(recommended_df)
    if verbose:
        if items_df is None:
            raise Exception('"items_df" is required in verbose mode')
        # print(recommended_df)
        # lower case the Book-Title of books DataFrame if not to avoid errors
        items_df['Title'] = items_df['Title'].str.lower()

        # merge recommended items with other details
        recommended_df = recommended_df.merge(items_df, how='left',
                                              # left_on = 'index',
                                              left_index=True,
                                              right_on='Title')[['recStrength', 'ISBN', 'Title',
                                                                 'Pub_Year', 'Publisher',
                                                                 'Image_Url', 'Author']]
        recommended_df = recommended_df.drop_duplicates(
            subset='Title', keep='first')
    return recommended_df


def recommend(name):
    name = name.lower()
    name2 = name.lower().strip()
    name3 = name.replace(',', '')
    name4 = name2.replace(':', '')
    global title
    title = books[books['Title'].str.contains(
        f'{name}|{name2}|{name3}|{name4}')]['Title'].values
    try:
        title = title[0]
        books_recommendations = recommend_items_by_item(
            title, pred_df, books, topn=6, verbose=True)
        return books_recommendations
    except Exception as error:
        return f"Oops! Book Not Found.....\n Try Again\n{error}"


app = Flask(__name__)


@app.route('/top_20_books')
def home():
    book_name = top_50_df.loc[:19, 'Book-Title']
    book_auth = top_50_df.loc[:19, 'Author']
    book_url = top_50_df.loc[:19, 'Image_Url']

    return render_template('home.html', b_name=book_name, author=book_auth, url=book_url)


# @app.route('/recommend_static')
# def recommend_ui():
#     return render_template('index.html')

# Added home route
@app.route('/')
def recommend_ui():
    return render_template('index.html')


@app.route('/recommend', methods=['post'])
def myapp():
    user_input = request.form.get('user_input')
    recommendation_df = recommend(user_input)
    try:
        rec_data = []
        recommendation_df = recommendation_df[[
            'Title', 'Pub_Year', 'Image_Url', 'Author']]
        for i in range(len(recommendation_df.index)):
            rec_data.append(recommendation_df.iloc[i].values)
    except:
        rec_data = [['Oops! Book not Found', '', '', 'Please Try Again']]

    return render_template('index.html', book_name=title, data=rec_data)

# tests is only for testing cases and IO


@app.route('/tests')
def test():
    '''This function is for testing results'''
    rec_data = []
    recommendation_df = recommend('1984')
    for i in range(len(recommendation_df.index)):
        rec_data.append(recommendation_df.iloc[i].values)
    return recommendation_df['Image_Url'].values[0]


if __name__ == '__main__':
    app.run(debug=True)
