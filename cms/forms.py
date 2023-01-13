from django import forms


class updatePosterForm(forms.Form):
    """
    used for checking if any field in the form is missing
    """

    posterID = forms.IntegerField(required=False)
    title = forms.CharField(widget=forms.Textarea,
                            required=True,
                            error_messages={'required': "Title is required"})
    abstract = forms.CharField(widget=forms.Textarea,
                               required=True,
                               error_messages={'required': "Abstract is required"})
    authorName = forms.CharField(max_length=128,
                                 required=True,
                                 error_messages={'required': "Author Name is required"})
    authorEmail = forms.CharField(max_length=128,
                                  required=True,
                                  error_messages={'required': "Author Email is required"})
    supervisorName = forms.CharField(max_length=128,
                                     required=True,
                                     error_messages={'required': "Supervisor Name is required"})
    programme_name = forms.CharField(max_length=128,
                                     required=True,
                                     error_messages={'required': "Programme is required"})
