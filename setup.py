from setuptools import setup

setup(name='pyTweetBot',
      version=1.0,
      description='A Twitter bot to collect articles and news from the Web and tweet/retweet it on your feed',
      url='https://github.com/nschaetti/pyTweetBot',
      author='Nils Schaetti',
      author_email='n.schaetti@gmail.com',
      license='GPL',
      packages=['config', 'db', 'directmessage', 'executor', 'friends', 'learning', 'mail', 'news', 'patterns',
                'retweet', 'stats', 'templates', 'tools', 'tweet', 'twitter'])
