"""tools to create a goodreads client"""

# for environment variables
import os

# for the goodreads api wrapper
from goodreads_wrapper_updates import GoodreadsClientImproved

# read in the key and secret from the environment
# (they will be there after secrets.sh is sourced)
gkey = os.environ.get('GOODREADS_KEY')
gsecret = os.environ.get('GOODREADS_SECRET')
gtoken = os.environ.get('GOODREADS_ACCESS_TOKEN')
gtoken_secret = os.environ.get('GOODREADS_ACCESS_TOKEN_SECRET')

# create goodreads client object
gc = GoodreadsClientImproved(gkey, gsecret)
gc.authenticate(gtoken, gtoken_secret)
