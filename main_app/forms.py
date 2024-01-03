from django import forms
from django.forms.widgets import DateInput, TextInput

from .models import *
from . import models


class FormSettings(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormSettings, self).__init__(*args, **kwargs)
        # Here make some changes such as:
        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'


class CustomUserForm(FormSettings):
    email = forms.EmailField(required=True)
    gender = forms.ChoiceField(choices=[('M', 'Male'), ('F', 'Female')])
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    address = forms.CharField(widget=forms.Textarea)
    password = forms.CharField(widget=forms.PasswordInput)
    widget = {
        'password': forms.PasswordInput(),
    }
    profile_pic = forms.ImageField()

    def __init__(self, *args, **kwargs):
        super(CustomUserForm, self).__init__(*args, **kwargs)

        if kwargs.get('instance'):
            instance = kwargs.get('instance').admin.__dict__
            self.fields['password'].required = False
            for field in CustomUserForm.Meta.fields:
                self.fields[field].initial = instance.get(field)
            if self.instance.pk is not None:
                self.fields['password'].widget.attrs['placeholder'] = "Fill this only if you wish to update password"

    def clean_email(self, *args, **kwargs):
        formEmail = self.cleaned_data['email'].lower()
        if self.instance.pk is None:  # Insert
            if CustomUser.objects.filter(email=formEmail).exists():
                raise forms.ValidationError(
                    "The given email is already registered")
        else:  # Update
            dbEmail = self.Meta.model.objects.get(
                id=self.instance.pk).admin.email.lower()
            if dbEmail != formEmail:  # There has been changes
                if CustomUser.objects.filter(email=formEmail).exists():
                    raise forms.ValidationError("The given email is already registered")

        return formEmail

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'gender',  'password','profile_pic', 'address' ]


class MerchantForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(MerchantForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Merchant
        fields = CustomUserForm.Meta.fields + \
            ['course', 'session']


class AdminForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(AdminForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Admin
        fields = CustomUserForm.Meta.fields


class ProviderForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(ProviderForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Provider
        fields = CustomUserForm.Meta.fields + \
            ['course' ]


class ComplianceForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(ComplianceForm, self).__init__(*args, **kwargs)

    class Meta:
        fields = ['name']
        model = Compliance


class QuestionnaireForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(QuestionnaireForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Questionnaire
        fields = ['name', 'provider', 'compliance', 'question']

# class QuestionnaireassignForm(forms.ModelForm):
#     def __init__(self, *args, **kwargs):
#         super(QuestionnaireassignForm, self).__init__(*args, **kwargs)
#     #latest
#     name = forms.ModelMultipleChoiceField(
#         queryset=Questionnaire.objects.all(),
#         widget=forms.SelectMultiple,
#         required=False,  # Make it optional
#     )
#     merchant = forms.ModelMultipleChoiceField(
#         queryset=Merchant.objects.all(),
#         widget=forms.SelectMultiple,
#         required=False,  # Make it optional
#     )
    
#     class Meta:
#         model = Questionnaire
#         fields = ['name', 'merchant']  
class QuestionnaireassignForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(QuestionnaireassignForm, self).__init__(*args, **kwargs)

        # Retrieve the distinct 'q_id' and 'name' values
        questionnaires = Questionnaire.objects.values('q_id', 'name').distinct()

        # Create a list of tuples containing the 'q_id' as the value and 'name' as the label
        questionnaire_choices = [(q['q_id'], q['name']) for q in questionnaires]

        # Set the choices for the 'name' field
        self.fields['name'].choices = questionnaire_choices
    
    name = forms.ModelMultipleChoiceField(
        queryset=Questionnaire.objects.all(),
        widget=forms.SelectMultiple,
        required=False,
        label='Select Questionnaires',
        to_field_name='q_id',
    )
    
    merchant = forms.ModelMultipleChoiceField(
        queryset=Merchant.objects.all(),
        widget=forms.SelectMultiple,
        required=False,
        label='Select Merchants',
    )
    
    class Meta:
        model = Questionnaire
        fields = ['name', 'merchant']

# class QuestionnaireassignForm(forms.ModelForm):
#     def __init__(self, *args, **kwargs):
#         super(QuestionnaireassignForm, self).__init__(*args, **kwargs)
    
#     name = forms.ModelMultipleChoiceField(
#         queryset=Questionnaire.objects.values('q_id').distinct(),
#         widget=forms.SelectMultiple,
#         required=False,
#         label='Select Questionnaires',
#     )
#     merchant = forms.ModelMultipleChoiceField(
#         queryset=Merchant.objects.all(),
#         widget=forms.SelectMultiple,
#         required=False,
#         label='Select Merchants',  
#     )
    
    class Meta:
        model = Questionnaire
        fields = ['name', 'merchant']        


class SessionForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(SessionForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Session
        fields = '__all__'
        widgets = {
            'start_year': DateInput(attrs={'type': 'date'}),
            'end_year': DateInput(attrs={'type': 'date'}),
        }


class LeaveReportStaffForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(LeaveReportStaffForm, self).__init__(*args, **kwargs)

    class Meta:
        model = LeaveReportStaff
        fields = ['date', 'message']
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
        }


class FeedbackStaffForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(FeedbackStaffForm, self).__init__(*args, **kwargs)

    class Meta:
        model = FeedbackStaff
        fields = ['feedback']


class LeaveReportStudentForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(LeaveReportStudentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = LeaveReportStudent
        fields = ['date', 'message']
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
        }


class FeedbackStudentForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(FeedbackStudentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = FeedbackStudent
        fields = ['feedback']


class MerchantEditForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(MerchantEditForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Merchant
        fields = CustomUserForm.Meta.fields 


class ProviderEditForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(ProviderEditForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Provider
        fields = CustomUserForm.Meta.fields


class EditResultForm(FormSettings):
    session_list = Session.objects.all()
    session_year = forms.ModelChoiceField(
        label="Session Year", queryset=session_list, required=True)

    def __init__(self, *args, **kwargs):
        super(EditResultForm, self).__init__(*args, **kwargs)

    class Meta:
        model = StudentResult
        fields = ['session_year', 'subject', 'student', 'test', 'exam']

class YourResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ['response']


#todos
# class TodoForm(forms.ModelForm):
#     class Meta:
#         model=Todo
#         fields=["title","is_finished"]

#issue book

class IssueBookForm(forms.Form):
    isbn2 = forms.ModelChoiceField(queryset=models.Book.objects.all(), empty_label="Book Name [ISBN]", to_field_name="isbn", label="Book (Name and ISBN)")
    name2 = forms.ModelChoiceField(queryset=models.Merchant.objects.all(), empty_label="Name ", to_field_name="", label="Student Details")
    
    isbn2.widget.attrs.update({'class': 'form-control'})
    name2.widget.attrs.update({'class':'form-control'})
