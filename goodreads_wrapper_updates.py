"""updates to the goodreads wrapper found at 
https://github.com/sefakilic/goodreads"""

from goodreads import group, client


class GoodreadsGroupImproved(group.GoodreadsGroup):
    """update the GoodReadsGroup class with needed features"""
    @property
    def members(self):
        """Members of the group"""
        return self._group_dict['members']['group_user']


    # def reviews(self, page=1):
    #     """Get all books and reviews on user's shelves"""
    #     resp = self._client.session.get("/review/list.xml",
    #                                     {'v': 2, 'id': self.gid, 'page': page})
    #     return [review.GoodreadsReview(r) for r in resp['reviews']['review']]


class GoodreadsClientImproved(client.GoodreadsClient):
    """update the goodreads client to use my group class"""

    def group(self, group_id):
        """Get info about a group"""
        resp = self.request("group/show", {'id': group_id})
        return GoodreadsGroupImproved(resp['group'])
