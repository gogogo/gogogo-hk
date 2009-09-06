from google.appengine.ext import db
from django import forms

class NumberListProperty(db.ListProperty):

    def validate(self, value):
        if isinstance(value,basestring):
            try:
                value = [self.item_type(v) for v in value.split(",")]
            except ValueError:
                raise forms.ValidationError("Contains non-numeric value")
                    
        return super(NumberListProperty, self).validate(value)

    def get_value_for_form(self, instance):
        """Extract the property value from the instance for use in a form.
        """

        value = super(NumberListProperty, self).get_value_for_form(instance)
        if not value:
            return None
        if isinstance(value, list):
            value = ','.join([str(v) for v in value])
        return value

    def make_value_from_form(self, value):
        """Convert a form value to a property value.

        This breaks the string into lines.
        """
        if not value:
            return []
        if isinstance(value, basestring):
            new_value = []
            for v in value.split(','):
                try:
                    new_value.append(self.item_type(v))
                except ValueError:
                    pass
                
            value = new_value
            
        return value
