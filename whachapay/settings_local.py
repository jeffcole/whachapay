from settings import *

# Local Django settings for whachapay project.

DATABASES = {'default': dj_database_url.config(default='sqlite:////'
                                               + os.path.join(SITE_ROOT,
                                                              'sqlite3.db'))}
