# import the standard Django Forms
# from built-in library
from django import forms


# creating a form
class InputForm(forms.Form):

    input_url = forms.CharField(max_length=200, widget=forms.Textarea(attrs={'rows':5}), initial="https://google.com\r\nhttps://www.bing.com/")
    

