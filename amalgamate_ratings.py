"""tests using the goodreads API wrapper from 
    https://github.com/sefakilic/goodreads
"""

# for the goodreads client object
from goodreads_tools import gc

# for checking types 
from collections import OrderedDict

# keyword for user groups about classics
CLASSICS_GROUP_KEYWORD = 'classic'

###################### functions ###############################
def add_reviews_by_user(user_ids, ratings):
    """modify the ratings dict by adding all ratings for user_id"""

    for user_id in user_ids: 
        print 'processing user', user_id

        # get the user object
        user = gc.user(user_id)

        # if the user is private, we ain't getting any reviews. Move along
        if 'private' in user._user_dict and user._user_dict['private'] == 'true':
            print '\tprivate, skipping...'
            return

        # page through the results, starting with page 1
        i = 1

        # for debugging
        rating_count = 0

        # placeholder 
        reviews = True

        while reviews: 

            print 'review page', i

            # the goodreads python wrapper throws a KeyError (or sometimes 
            # TypeError) if there are no reviews
            try:
              reviews = user.reviews(page=i)
            except KeyError, TypeError:
              reviews = []

            # cycle through reviews
            for review in reviews:

                # if the review is not workable by the goodreads module, skip
                try:
                    # if the rating is 0, that means it's a text-only review. Skip. 
                    if review.rating == '0':
                        continue
                except: 
                    continue

                isbn = review.book['isbn']

                # eliminate books without an isbn
                # isbn will be a string if it exists, otherwise an OrderedDict
                if isinstance(isbn, OrderedDict):
                    continue

                # initialize if we haven't seen this book before
                if isbn not in ratings:
                    ratings[isbn] = {'title': review.book['title'].encode('unicode-escape'),
                                     'ratings': []}

                # add this rating
                rating_tuple = (user_id, review.rating)
                ratings[isbn]['ratings'].append(rating_tuple)

                rating_count += 1 # debugging

            # increment the page
            i += 1
        
        print '\tfound', rating_count, 'ratings'


def get_classics_users():

    # to store user ids we find
    users = set()

    # get a list of groups related to our classics keyword
    groups = gc.find_groups(CLASSICS_GROUP_KEYWORD)

    # make sure we get all pages
    i = 1

    # while groups:
    while groups and i == 1: # for testing

        print '*' * 20, 'page', i

        # for group_dict in groups: 
        for group_dict in groups[0:1]:  # for testing

            # get actual group object
            # group = gc.group(group_dict['id'])
            group = gc.group(95455) # testing

            # note: some group names are unicode (greek!) and don't translate well to ascii
            print 'processing group', group.gid, group.title.encode('unicode-escape')

            # make sure we get all pages of members
            members = set()

            member_page = group.members

            for member in member_page:
                
                # need to guard against "members" come back as strings 
                # (such as 'comment_count')
                if isinstance(member, OrderedDict):
                    users.add(member['user']['id']['#text'])

                    members.add(member['user']['id']['#text'])

            print 'found', len(members), 'members. Actual count:', group.users_count

        # get the next page
        i += 1
        groups = gc.find_groups(CLASSICS_GROUP_KEYWORD, page=i)

    return users

def print_ratings(rating_data, outfile_name):
    """given a ratings dict, print formatted data to file"""

    outfile = open(outfile_name, 'w')

    for isbn, data in rating_data.items():
        outfile.write('*' * 10 + isbn + '*' * 10 + '\n')
        outfile.write('*' + data['title'] + '\n')
        for rating in data['ratings']:
            outfile.write('\t' + rating[1] + ' ' + rating[0] + '\n\n')

    outfile.close()

####################### main ####################################

# global dictionary to store ratings (this should be stored in db ultimately,
# but this is a quick and dirty proof of concept...)
# keys: isbn numbers
# values: dict with keys
#           book_title (string)
#           ratings (list of tuples -- user_id, rating)
rating_data = {}

# get user ids for classics groups
user_ids = get_classics_users()

# get reviews for these users
add_reviews_by_user(user_ids, rating_data)

# print the results
print_ratings(rating_data, 'ratings.txt')


