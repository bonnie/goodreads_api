"""tests using the goodreads API wrapper from 
    https://github.com/sefakilic/goodreads
"""

# for environment variables
import os

# for the goodreads api wrapper
from goodreads import client

from collections import OrderedDict

# keyword for user groups about classics
CLASSICS_GROUP_KEYWORD = 'classic'

###################### functions ###############################
def add_reviews_by_user(user_id, ratings):
    """modify the ratings dict by adding all ratings for user_id"""

    print 'processing user', user_id

    # get the user object
    user = gc.user(user_id)

    # if the user is private, we ain't getting any reviews. Move along
    if 'private' in user._user_dict and user._user_dict['private'] == 'true':
        return

    # cycle through reviews
    for review in user.reviews():

        isbn = review.book['isbn']

        # eliminate books without an isbn
        if isinstance(isbn, OrderedDict):
            return

        # initialize if we haven't seen this book before
        if isbn not in ratings:
            ratings[isbn] = {'title': review.book['title'].encode('unicode-escape'),
                             'ratings': []}

        # add this rating
        rating_tuple = (user_id, review.rating)
        ratings[isbn]['ratings'].append(rating_tuple)

def get_classics_users():

    # to store user ids we find
    users = set()

    # get a list of groups related to our classics keyword
    groups = gc.find_groups(CLASSICS_GROUP_KEYWORD)
    # for group_dict in groups: 
    for group_dict in groups[0:1]:  # for testing

        # get actual group object
        group = gc.group(group_dict['id'])
        print group.gid

        # note: some group names are unicode (greek!) and don't translate well to ascii
        print 'processing group', group.title.encode('unicode-escape')

        for member in group.members:
            
            # sometimes "members" come back as strings (such as 'comment_count')

            if isinstance(member, OrderedDict):
                users.add(member['user']['id']['#text'])

    return users

####################### main ####################################

# read in the key and secret from the environment
# (they will be there after secrets.sh is sourced)
gkey = os.environ.get('GOODREADS_KEY')
gsecret = os.environ.get('GOODREADS_SECRET')
gtoken = os.environ.get('GOODREADS_ACCESS_TOKEN')
gtoken_secret = os.environ.get('GOODREADS_ACCESS_TOKEN_SECRET')

# create goodreads client object
gc = client.GoodreadsClient(gkey, gsecret)
gc.authenticate(gtoken, gtoken_secret)

# global dictionary to store ratings (this should be stored in db ultimately,
# but this is a quick and dirty proof of concept...)
# keys: isbn numbers
# values: dict with keys
#           book_title (string)
#           ratings (list of tuples -- user_id, rating)
rating_data = {}

user_ids = get_classics_users()
for user in user_ids:
    add_reviews_by_user(user, rating_data)

for isbn, data in rating_data.items():
    print '*' * 10, isbn, '*' * 10
    print '*', data['title']
    for rating in data['ratings']:
        print '\t', rating[1], rating[0]
    print

