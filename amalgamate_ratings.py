"""tests using the goodreads API wrapper from 
    https://github.com/sefakilic/goodreads
"""

# for the goodreads client object
from goodreads_tools import gc

# for checking types 
from collections import OrderedDict

# keyword for user groups about classics
CLASSICS_GROUP_KEYWORD = 'classic'

# for db connection
from model import app, db, connect_to_db, User, Book, Group, Rating

# for tracking how long things take
from datetime import datetime

###################### functions ###############################
def print_time():
    now = datetime.now()
    print "=" * 20
    print datetime.strftime(now, '%m-%d %H:%M:%S')
    print "=" * 20

def add_reviews_by_user(user_id):
    """modify the ratings dict by adding all ratings for user_id"""

    print '\t\tprocessing user', user_id

    # skip if the user is already in the db
    if User.query.get(user_id):
        print '\t\t\talready added, skipping...'
        return

    # start a user row
    user_row = User(user_id=user_id)

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

        user_row.process_success = False
        db.session.add(user_row)
        return

    # if the user is private, we ain't getting any reviews. Move along
    if 'private' in user._user_dict and user._user_dict['private'] == 'true':
        print '\t\t\tprivate, skipping...'

        user_row.private = True
        user_row.success = False
        db.session.add(user_row)
        return

    # page through the results, starting with page 1
    i = 1

    # for debugging
    rating_count = 0

    reviews = user.get_all_reviews()

    print "\t\t\tgot", len(reviews), "reviews"

    # cycle through reviews
    for review in reviews:

        # if we got this far, it's time to add the user
        user_row.success = True
        user_row.private = False
        db.session.add(user_row)

        # if the rating is 0, that means it's a text-only review. Skip. 
        if review.rating == '0':
            continue

        isbn = review.book['isbn']

        # eliminate books without an isbn
        # isbn will be a string if it exists, otherwise an OrderedDict
        if isinstance(isbn, OrderedDict):
            continue

        # add this book if we haven't seen it before
        book = Book.query.get(isbn)
        if not book:
            title = review.book['title'].encode('unicode-escape')[:256]
            book = Book(book_id=isbn, title=title)
            db.session.add(book)

        # add this rating
        rating = Rating(user_id=user_id, book_id=isbn, score=review.rating)
        db.session.add(rating)

        rating_count += 1 # debugging

    print '\t\t\tfound', rating_count, 'ratings'

    # commit the ratings before returning
    db.session.commit()


def process_classics_users():

    # just to get a sense of timing
    print_time()

    # get a list of groups related to our classics keyword
    groups = gc.find_groups(CLASSICS_GROUP_KEYWORD)

    # make sure we get all pages
    gpage = 1

    while groups:
    # while groups and gpage == 1: # for testing

        print '*' * 10, 'group page', gpage

        for group_dict in groups: 
        # for group_dict in groups[0:1]:  # for testing

            # skip this group if its already been processed
            if Group.query.get(group_dict['id']):
                print '\t\t\talready added group id', group_dict['id'], ', skipping...'
                continue

            # get actual group object
            group = gc.group(group_dict['id'])
            # group = gc.group(95455) # testing

            # note: some group names are unicode (greek!) and don't translate well to ascii
            group_name = group.title.encode('unicode-escape')
            print '***** processing group', group.gid, group_name

            # make sure we get all pages of members
            mpage = 1
            member_results = True

            # keep track of whether it was processed successfully
            process_success = True

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

                    # record that it was not successfully processed
                    process_success=False
                    break

                for member in member_results:
                    user_id = member['id']['#text']

                    # skip this user if already processed
                    if User.query.get(user_id):
                        continue

                    # otherwise, add the reviews (and  add the user to the db)
                    success = add_reviews_by_user(user_id)

                mpage += 1

            # we're done with this group -- put it in the db so we can skip it 
            # if we re-process
            group_row = Group(group_id=group.gid, 
                              group_name=group_name, 
                              process_success=process_success)
            db.session.add(group_row)
            db.session.commit()

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

# establish db
connect_to_db(app)

# get user ids from classics groups and their reviews
process_classics_users()

# print the results to a 'ratings.txt' file
print_ratings('ratings.txt')


