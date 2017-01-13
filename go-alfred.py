import webapp2
import jinja2
import os
import random

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import mail

jinja_environment = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class Entry(db.Model):
  author = db.StringProperty()
  title = db.StringProperty()
  content = db.TextProperty()
  category = db.CategoryProperty(default="Work_English", choices=["Work_English", "Work_Spanish", "Personal_English", "Personal_Spanish"])
  published = db.DateProperty(auto_now_add=True)
  updated = db.DateProperty(auto_now=True)
  
class MainPage(webapp2.RequestHandler):
  def get(self):
    entries_query = db.GqlQuery("SELECT * FROM Entry WHERE category = :1 ORDER BY published DESC", 'Work_English')
    entries = entries_query.fetch(1)
    
    template_values = {
        'entries': entries,
    }
    template = jinja_environment.get_template('templates/index.html')
    self.response.out.write(template.render(template_values))
    
class NewBlogEntry(webapp2.RequestHandler):
  def get(self):
    
    if users.is_current_user_admin():
      url = users.create_logout_url('/')
      url_linktext = 'Logout'

    template_values = {
      'url': url,
      'url_linktext': url_linktext,
    }
    
    template = jinja_environment.get_template('templates/new.html')
    self.response.out.write(template.render(template_values))

class AddBlogEntry(webapp2.RequestHandler):
  def post(self):
    entry = Entry()
    entry.author=self.request.get('author')
    entry.title=self.request.get('title')
    entry.content=self.request.get('content')
    entry.category=self.request.get('category')
    entry.put()
    #self.response.out.write("added to data store")
    self.redirect('/')
    
class DelBlogEntry(webapp2.RequestHandler):
  def get(self):
    id = int(self.request.get('id'))
    entry_key = db.Key.from_path('Entry', id)
    db.delete(entry_key)
    #self.response.out.write("deleted from data store")
    self.redirect('/')
    
class EditBlogEntry(webapp2.RequestHandler):
  def get(self):
    id = int(self.request.get('id'))
    entry_key = db.Key.from_path('Entry', id)
    entry = db.get(entry_key)
    template_values = {
        'entry': entry,
    }
    
    template = jinja_environment.get_template('templates/edit.html')
    self.response.out.write(template.render(template_values))
    
class ViewBlogEntry(webapp2.RequestHandler):
  def get(self):
    id = int(self.request.get('id'))
    entry_key = db.Key.from_path('Entry', id)
    entry = db.get(entry_key)
    
    template_values = {
      'entry': entry,
    }
    template = jinja_environment.get_template('templates/view.html')
    self.response.out.write(template.render(template_values))
    
class UpdateBlogEntry(webapp2.RequestHandler):
  def post(self):
    id = int(self.request.get('id'))
    entry_key = db.Key.from_path('Entry', id)
    entry = db.get(entry_key)
    entry.author = self.request.get('author')
    entry.title = self.request.get('title')
    entry.content = self.request.get('content')
    entry.category = self.request.get('category')
    entry.put()
    self.redirect('/sysadmin')
    
class ContactLink(webapp2.RequestHandler):
  def get(self):
    # Numbers for the verification operation fiels in the form to prevent againt spammers
    verification_values = {'num1': random.randint(1,9), 'num2': random.randint(1,9)}
    
    template_values = {
      'verification_values': verification_values,
    }
    
    template = jinja_environment.get_template('templates/contact.html')
    self.response.out.write(template.render(template_values))
    
class SysAdmin(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    
    if user:
      if users.is_current_user_admin():
        url = users.create_logout_url('/')
        url_linktext = 'Logout'
        entries_query = db.GqlQuery("SELECT * FROM Entry ORDER BY published DESC")
        entries = entries_query.fetch(10)
    
        template_values = {
          'entries': entries,
          'url': url,
          'url_linktext': url_linktext,
        }
        template = jinja_environment.get_template('templates/sysadmin.html')
        self.response.out.write(template.render(template_values))
      else:
        self.redirect('/')
    else:
      self.redirect('/')
      
class WorkLink(webapp2.RequestHandler):      
  def get(self):
    entries_query = db.GqlQuery("SELECT * FROM Entry WHERE category = :1 ORDER BY published DESC", 'Work_English')
    entries = entries_query.fetch(10)
    
    template_values = {
        'entries': entries,
    }
    template = jinja_environment.get_template('templates/work.html')
    self.response.out.write(template.render(template_values))

class PersonalLink(webapp2.RequestHandler):
  def get(self):
    entries_query = db.GqlQuery("SELECT * FROM Entry WHERE category = :1 ORDER BY published DESC", 'Personal_English')
    entries = entries_query.fetch(10)
    
    template_values = {
        'entries': entries,
    }
    template = jinja_environment.get_template('templates/personal.html')
    self.response.out.write(template.render(template_values))
    
    
class GetContact(webapp2.RequestHandler):
  def post(self):
    #Get Contact Form Data
    contact_name = self.request.get('contact_name')
    contact_email = self.request.get('contact_email')
    contact_comments = self.request.get('contact_comments')
    
    message = mail.EmailMessage(sender="Google App Engine Blog",
                                subject="App Engine Contact Data Submitted")
    message.to = 'YOUR_EMAIL_ADDRESS'
    message.body = """A visitor submitted the following data: \n Name: %s \n Email: %s \n Comments: %s """ % (contact_name, contact_email, contact_comments)
    message.send()
    self.redirect('/')

class ArchiveLink(webapp2.RequestHandler):
  def get(self):
    entries_query = db.GqlQuery("SELECT * FROM Entry ORDER BY published DESC")
    entries = entries_query.run()
	
    template_values = {
        'entries': entries,
    }
	
    template = jinja_environment.get_template('templates/archive.html')
    self.response.out.write(template.render(template_values))
		
		
class XMLFeed(webapp2.RequestHandler):
	def get(self):
		entry = Entry()
		xmldata = entry.to_xml()
		self.response.headers['Content-Type'] = "text/xml"
		self.response.out.write(xmldata)


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/new', NewBlogEntry),
                               ('/add', AddBlogEntry),
                               ('/del', DelBlogEntry),
                               ('/edit', EditBlogEntry),
                               ('/update', UpdateBlogEntry),
                               ('/view', ViewBlogEntry),
                               ('/sysadmin', SysAdmin),
                               ('/work', WorkLink),
                               ('/personal', PersonalLink),
                               ('/contact', ContactLink),
                               ('/getcontact', GetContact),
							   ('/xmlfeed', XMLFeed),
							   ('/archive', ArchiveLink)],
                              debug=False)
