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
def add_reviews_by_user(user_id, ratings):
    """modify the ratings dict by adding all ratings for user_id"""

    print '\t\tprocessing user', user_id

    # get the user object. This doesn't work for some (deleted?) users
    try:
        user = gc.user(user_id)
    except Exception as e:
        try:
            err_string = str(e)
        except:
            err_string = '<no error string>'

        print "~~~~~~~~ ERROR: couldn't get user id", user_id, ":", err_string
        print "~~~~~~~~ Moving on."
        return

    # if the user is private, we ain't getting any reviews. Move along
    if 'private' in user._user_dict and user._user_dict['private'] == 'true':
        print '\t\t\tprivate, skipping...'
        return

    # page through the results, starting with page 1
    i = 1

    # for debugging
    rating_count = 0

    reviews = user.get_all_reviews()

    print "\t\t\tgot", len(reviews), "reviews"

    # cycle through reviews
    for review in reviews:

        # if the rating is 0, that means it's a text-only review. Skip. 
        if review.rating == '0':
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

    print '\t\t\tfound', rating_count, 'ratings'


def process_classics_users(ratings):

    # to store user ids we find
    users = set()

    # get a list of groups related to our classics keyword
    groups = gc.find_groups(CLASSICS_GROUP_KEYWORD)

    # make sure we get all pages
    gpage = 1

    while groups:
    # while groups and gpage == 1: # for testing

        print '*' * 10, 'group page', gpage

        for group_dict in groups: 
        # for group_dict in groups[0:1]:  # for testing

            # get actual group object
            group = gc.group(group_dict['id'])
            # group = gc.group(95455) # testing

            # note: some group names are unicode (greek!) and don't translate well to ascii
            print '***** processing group', group.gid, group.title.encode('unicode-escape')

            # make sure we get all pages of members
            mpage = 1
            member_results = True

            while member_results:

                print '\tmember page', mpage

                try:
                    member_results = group.get_members(page=mpage)
                except Exception as e:
                    try:
                        err_string = str(e)
                    except:
                        err_string = '<no error string>'

                    print '~~~~~~~~ ERROR: problem getting members:', err_string
                    print "~~~~~~~~ Moving on."
                    break

                for member in member_results:
                    user_id = member['id']['#text']
                    if user_id not in users:
                        add_reviews_by_user(user_id, ratings)
                        users.add(user_id)

                mpage += 1

        # get the next page
        gpage += 1
        groups = gc.find_groups(CLASSICS_GROUP_KEYWORD, page=gpage)


def print_ratings(rating_data, outfile_name):
    """given a ratings dict, print formatted data to file"""

    outfile = open(outfile_name, 'w')

    for isbn, data in rating_data.items():
        outfile.write('*' * 10 + isbn + '*' * 10 + '\n')
        outfile.write('* ' + data['title'] + '\n')
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

# get user ids from classics groups and their reviews
process_classics_users(rating_data)

# print the results
print_ratings(rating_data, 'ratings.txt')


