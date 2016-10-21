"""updates to the goodreads wrapper found at 
https://github.com/sefakilic/goodreads"""

from goodreads import group, client, user


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


   # def reviews(self, page=1):
   #      """Get all books and reviews on user's shelves"""
   #      resp = self._client.session.get("/review/list.xml",
   #                                      {'v': 2, 'id': self.gid, 'page': page})
   #      return [review.GoodreadsReview(r) for r in resp['reviews']['review']]

 

    def get_members(self, page=1):
        """Get all books and reviews on user's shelves"""

        # URL: https://www.goodreads.com/group/members/GROUP_ID.xml   
        resp = self._client.session.get('/group/members/{}.xml'.format(self.gid),
                                        {'v': 2, 'page': page})

        # return empty list if there's no group_user key (that means there are no
        # users on this page)
        if 'group_users' not in resp or 'group_user' not in resp['group_users']:
            return []

        # there's not enough data in the user dict responses to make user objects
        # (missing user_name, for example), so just return the list of OrderedDicts
        return resp['group_users']['group_user']


class GoodreadsClientImproved(client.GoodreadsClient):
    """update the goodreads client to use my group class"""

    def group(self, group_id):
        """Get info about a group, using the GoodreadsGroupImproved class"""
        resp = self.request("group/show", {'id': group_id})
        return GoodreadsGroupImproved(resp['group'], self)
