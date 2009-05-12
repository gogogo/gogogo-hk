from google.appengine.ext import db
from ragendja.dbutils import KeyListProperty
from django import forms
from django.utils.safestring import mark_safe

class MultiLangStringInput(forms.Widget):	
	def __init__(self, attrs=None):
		self.widgets = [ forms.TextInput() , forms.TextInput() , forms.TextInput()]
		self.lang_code = ["English" , "Traditional Chinese" , "Simpified Chinese"]
		super(MultiLangStringInput, self).__init__(attrs)
		
	def render(self, name, value, attrs=None):
		output = []
		new_attrs = self.build_attrs(attrs)

		id_ = new_attrs.get('id', None)
		
		for i, widget in enumerate(self.widgets):
			try:
				widget_value = value[i]
			except IndexError:
				widget_value = None
				
			new_attrs = dict(new_attrs,id='%s_%s' % (id_, i))
			
			if "style" not in new_attrs :
				new_attrs['style'] = 'display : block'
			output.append("<div>%s</div>" % self.lang_code[i])
			output.append(widget.render(name + '_%s' % i, widget_value, new_attrs))
		
		HTML = "<div style='display : block;float : left'> %s </div>"	 %  u''.join(output)
		return mark_safe(HTML)
	
class MultiLangStringProperty(db.StringListProperty):
	
	def __init__ (self, *args, **kwargs):
		db.StringListProperty.__init__(self,*args,**kwargs)

	def get_form_field(self, **kwargs):
		attrs = {
		'form_class': forms.CharField,
        'widget' :  MultiLangStringInput}
		attrs.update(kwargs)
		return db.StringListProperty.get_form_field(self,**attrs)

class Agency(db.Model):
	"""
		Public transportation agency
	"""
	name = MultiLangStringProperty()
	
	url = db.StringProperty()
	
	timezone = db.StringProperty()
	
	phone = db.PhoneNumberProperty()
	

class Stops(db.Model):
	# An ID that uniquely identifies a stop or station. Multiple routes may use the same stop. 
	sid = db.StringProperty()
	
	# Optional field
	code = db.StringProperty()
	
	# name of the Stop (Multiple language)
	name = db.StringListProperty()
	
	desc = db.StringListProperty()

	# latitude and longitude value, it won't use the indexing function from BigTable. Use geohash instead
	latlng = db.GeoPtProperty()
	
	geohash = db.StringProperty()
	
	# TRUE if the geo position data is accuracy enough 
	accuracy = db.BooleanProperty()
	
	url = db.LinkProperty()
	
	location_type = db.IntegerProperty()
	
	parent_station = db.SelfReferenceProperty()
	
class Routes(db.Model):	
	rid = db.StringProperty()
	
	#agency = db.ReferenceProperty(agency)
	
	short_name = db.StringListProperty()
	
	long_name = db.StringListProperty()
	
	desc = db.StringListProperty()
	
	type = db.IntegerProperty()
	
	url = db.LinkProperty()
	
	color = db.StringProperty()
	
	text_color = db.StringProperty()
