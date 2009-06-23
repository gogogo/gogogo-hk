from django.core.urlresolvers import reverse
import cgi

class Pathbar:
	"""
	Create a path bar
	
	Template: gogogo/widgets/pathbar.html
	"""
	def __init__(self,sep=">"):
		self.path = []
		self.sep = sep
		
	def append(self,name,viewname,args):
		url = reverse(viewname,args=args)
		self.path.append((name , url ))
		
