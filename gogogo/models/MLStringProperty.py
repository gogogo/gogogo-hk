from google.appengine.ext import db
from ragendja.dbutils import KeyListProperty
from django import forms
from django.utils.safestring import mark_safe
from django.conf import settings
from TitledStringListProperty import TitledStringListProperty
from django.utils.translation import ugettext_lazy as _
from ragendja.dbutils import get_object
from gogogo.geo.geohash import Geohash
import re

class MLStringProperty(TitledStringListProperty):
    """
        Multi-language string property
    """
    def __init__ (self,*args,**kwargs):
        fields = self.get_lang_list()
        super(MLStringProperty,self).__init__(fields,*args,**kwargs)

    def trans(value,lang=0):
        """
            Translate a MLTextProperty value to a string for specific language.
            If no such translation existed , it will return the default language
            (The first language)
        """
        
        try:
            ret = value[lang]
        except IndexError:
            try:
                ret = value[0]
            except IndexError: #Value is none
                ret = ""
        
        return ret
        
    trans = staticmethod(trans)

    def to_key_name(value):
        """
        Convert the property into a key_name for bigtable.
        """
        pattern = re.compile("[a-z0-9]*")
        ret = None
        for item in value:
            m =  pattern.findall(item.lower())
            key_name = "".join(m)
            key_name.lstrip("_") # Remove leading "_". Avoid "__*__" format
            try:
                if key_name[0].isdigit():
                    key_name = "_" + key_name # Add single "_"
            except:
                pass
            
            if len(key_name) >= 3: # The key name should at last contains 3 char
                ret = key_name
                break
                
        return ret
        
    to_key_name = staticmethod(to_key_name)
	
    def get_current_lang(request):
        """
        Get the current language 
        """
        ret = 0
        for (i,lang) in enumerate(settings.LANGUAGES):
            if lang[0] == request.LANGUAGE_CODE:
                ret = i
                break
        return ret
        
    get_current_lang = staticmethod(get_current_lang)

    def get_lang_list():
        """
        Get a list of language (with full name). The returned 
        data can be used with TitledStringListProperty
        """
        
        fields = []
        for f in settings.LANGUAGES:
            fields.append(f[1])
            
        return fields

    get_lang_list = staticmethod(get_lang_list)
