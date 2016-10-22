"""updates to the goodreads wrapper found at 
https://github.com/sefakilic/goodreads"""

from goodreads import group, client, user, review
from collections import OrderedDict


class GoodreadsUserImproved(user.GoodreadsUser):
    """overload reviews function to return a list regardless"""

    def get_all_reviews(self):
        """Get all books and reviews on user's shelves. """

        # TODO: make this code less repetitive

        reviews = []
        page = 1

        # get the fist page
        resp = self._client.session.get("/review/list.xml",
                                {'v': 2, 'id': self.gid, 'page': page})

        review_count = resp['reviews']['@total']
        review_start = resp['reviews']['@start']
        review_end = resp['reviews']['@end']
       
        if review_end == '0':
            # there are no results for this page
            return []

        if review_count == '1':
            # only one review for this user
            # return a list of the (one) OrderedDict
            return [review.GoodreadsReview(resp['reviews']['review'])]

        # if we get here, there's another page to consider
        while int(review_end) < int(review_count):

            page += 1

            resp = self._client.session.get("/review/list.xml",
                                    {'v': 2, 'id': self.gid, 'page': page})

            review_start = resp['reviews']['@start']
            review_end = resp['reviews']['@end']

            if review_start == review_end:
                # only one review in this page
                # return a list of the (one) OrderedDict
                reviews.append(review.GoodreadsReview(resp['reviews']['review']))

                # there are no pages after this, so break
                break

            else:
                # this will be a list if the count is > 1
                reviews.extend([review.GoodreadsReview(r) for r in resp['reviews']['review']])


        return reviews


class GoodreadsGroupImproved(group.GoodreadsGroup):
    """update the GoodReadsGroup class with needed features"""

    def __init__(self, group_dict, client):
        """overloading init to include an _client"""

        self._group_dict = group_dict
        self._client = client   # for later queries


    @property
    def members(self):
        """
        Members of the group 

        * corrects typo in source files: ['group_users']
        """
        return self._group_dict['members']['group_user']
 

    def get_members(self, page=1):
        """Get all books and reviews on user's shelves"""

        # URL: https://www.goodreads.com/group/members/GROUP_ID.xml   
        resp = self._client.session.get('/group/members/{}.xml'.format(self.gid),
                                        {'v': 2, 'page': page})

        # return empty list if there's no group_user key (that means there are no
        # users on this page)
        if 'group_users' not in resp or 'group_user' not in resp['group_users']:
            return []

        # if there's only one, it returns an OrderedDict, not a list of OrderedDicts.
        # make sure we return a list
        if isinstance(resp['group_users']['group_user'], OrderedDict):
            return [resp['group_users']['group_user']]

        # there's not enough data in the user dict responses to make user objects
        # (missing user_name, for example), so just return the list of OrderedDicts
        return resp['group_users']['group_user']


class GoodreadsClientImproved(client.GoodreadsClient):
    """update the goodreads client to use my group class"""

    def group(self, group_id):
        """Get info about a group, using the GoodreadsGroupImproved class"""
        resp = self.request("group/show", {'id': group_id})
        return GoodreadsGroupImproved(resp['group'], self)

    def user(self, user_id=None, username=None):
        """Get info about a member by id or username.

        If user_id or username not provided, the function returns the
        authorized user.
        """
        if not (user_id or username):
            return self.auth_user()
        resp = self.request("user/show", {'id': user_id, 'username': username})
        return GoodreadsUserImproved(resp['user'], self)