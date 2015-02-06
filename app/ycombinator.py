from BeautifulSoup import BeautifulSoup
from urllib import urlopen
import re
from datetime import datetime, timedelta
from models import User, Post
from app import db

class Ycombinator:    
    @property
    def user(self):
        if not User.query.filter_by(username='ycombinator').first():
            user = User('ycombinator', '_ycombinator_')
            db.session.add(user)
            db.session.commit()
        else:
            user = User.query.filter_by(username='ycombinator').first()
        return user
    
    def get_news(self):
        url = 'https://news.ycombinator.com/newest'
        soup = BeautifulSoup(urlopen(url))
        if not soup:
            return False
        tds = soup.findAll('td', {'class':'title'})
        if len(tds) < 2:
            return False
        td = tds[1]
        result = { 'text': str(td.a) }
        contents = td.parent.nextSibling.td.next.contents
        if len(contents) < 2:
            return False
        time = re.search(' (\d+) (minutes|minute|hour|hours) ago | ',
                         contents[-2]).groups()
        if not time or not time[0]:
            return False
        
        if 'minute' in time[1]:
            delta = timedelta(minutes=int(time[0]))
        elif 'hour' in time[1]:
            delta = timedelta(hours=int(time[0]))
        else:
            return False
        
        result['date'] = datetime.now() - delta   
        return result

    def add_news(self, channel_id):
        news = self.get_news()
        if news and not Post.query.filter_by(
                body=news['text'], channel_id=channel_id).all():
            post = Post(body = news['text'])
            post.user_id = self.user.id
            post.channel_id = channel_id
            db.session.add(post)
            db.session.commit()
