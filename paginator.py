import datetime, markdown, os


def fwrite(filename, text):
	"""Write content to file and close the file."""
	basedir = os.path.dirname(filename)
	if not os.path.isdir(basedir):
		os.makedirs(basedir)
	with open(filename, 'wb') as f:
		f.write(text.encode('utf8'))


class Page(object):
	
	def __init__(self, env, config, template_name):
		self.name = template_name
		self.permalink = ''
		self.date = datetime.datetime.now() #TODO
		self._filename = ''
		self._template = env.get_template(template_name)
		self._config = config
		self._env = env
		self._vars = {
			'site': config['site'],
			'page': self
		}
		self.render()


	def render(self, more_vars = {}):
		self._vars.update(more_vars)
		# There a better way?
		self._vars.update(self._template.make_module(self._vars).__dict__)

		# Convert Markdown to HTML and render the specified layout.
		if self.name.endswith('.md'):
			md = markdown.Markdown(extensions=['meta','codehilite','extra'])
			self._vars['content'] = md.convert(self._template.render(self._vars))
			meta = self.process_meta(md.Meta)
			self._vars.update(meta)
			layout = self._vars.get('layout', '')
			if layout != '':
				t = self._env.get_template(layout)
				if meta.has_key('content'):
					print('  Warning: Defined variable "content" is not allowed with "layout".')
				self.url = self.get_permalink()
				self._vars['content'] = t.render(self._vars)
		else:
			self.url = self.get_permalink()
			self._vars['content'] = self._template.render(self._vars)
			
	def get(self, key, default):
		return self._vars.get(key, default)
		
	def __getattribute__(self, name):
		if name != '_vars' and name in self._vars:
			return self._vars[name]
		return super(Page, self).__getattribute__(name)
		

	def process_meta(self, d):
		r = {}
		for k, v in d.items():
			r[k] = v[1:] if len(v) > 1 else v[0]
		return r

	def get_permalink(self, use_cache = True):
		if use_cache and self.permalink != '':
			return self.permalink
		elif self.name == 'index.html':
			self.permalink = '/'
		elif self.name.endswith('.xml'):
			self.permalink = '/' + self.name
		else:
			url = getattr(self, 'permalink', '')
			if url == '':
				self.permalink = self.name[:self.name.rfind('.')]
			elif url.startswith('/'):
				self.permalink = url
			else:
				# Permalinks are relative if they don't start with '/'
				d = os.path.dirname(self.name)
				self.permalink = os.path.join(d, url)
		return self.permalink
		
	def get_filename(self, use_cache = True):
		if use_cache and self._filename != '':
			return self._filename
		
		root = os.path.dirname(os.path.abspath(__file__))
		path = self.get_permalink(use_cache)
		if path.startswith('/'):
			path = path.lstrip('/')

		# XML files retain their filename, ignore permalink
		if self.name.endswith('.xml'):
			self._filename = os.path.join(root, self._config['output_dir'], self.name)
		else:
			self._filename = os.path.join(root, self._config['output_dir'], path, 'index.html')
			
		return self._filename

		
	def save(self, filename = ''):
		if filename == '':
			filename = self.get_filename()
		fwrite(filename, self.get('content', ''))


class Paginator(object):
	
	def __init__(self, env, config, page, posts):
		self.permalink = config['paginator']['permalink']
		self.first_permalink = page.get_permalink()
			
		# TODO: sort posts by date?

		items_per_page = config['paginator']['items_per_page']
		template_name = page.name
		self.pages = []
		self.all_posts = posts
		self.page_count = 1 + (len(posts) - 1) / items_per_page
		
		for i in range(1, self.page_count + 1):
			start = (i - 1) * items_per_page
			end = i * items_per_page
			self.posts = posts[start:end]
			print('  Doing page {}... {}'.format(i, self.posts))

			page = Page(env, config, template_name)
			self.page = i
			self.prev_permalink = ''
			self.next_permalink = ''
			if i > 1:
				page.permalink = self.permalink.replace(':num', str(i))
				if i == 2:
					self.prev_permalink = self.first_permalink
				else:
					self.prev_permalink = self.permalink.replace(':num', str(i-1))
			if i < self.page_count:
				self.next_permalink = self.permalink.replace(':num', str(i+1))
			
			page.render({'paginator': self})
			self.pages.append(page)
		
	def get_pages(self):
		return self.pages