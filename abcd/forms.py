from abcd.models import *
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms.fields import Field

class addIndividualForm(forms.ModelForm):
    individual_name = forms.CharField(required=False, max_length=200)
    class Meta:
        model = Stakeholders
        fields = ('individual_name',)

class addCommunityForm(forms.ModelForm):
    community_addr = forms.CharField(required=False, max_length=500)

    class Meta:
        model = Community
        fields = ('community_addr',)

class addTagForm(forms.ModelForm):
    tag_name = forms.CharField(required=False, max_length=200)
    class Meta:
        model = Tags
        fields = ('tag_name',)

class addAssetForm(forms.ModelForm):
    asset_name = forms.CharField(required=False, max_length=500)
    asset_details = forms.CharField(required=False, max_length=500)
    asset_address = forms.CharField(required=False, max_length=500)
    asset_contact = forms.CharField(required=False, max_length=500)

    class Meta:
        model = Assets
        fields = ('asset_name','asset_details','asset_address','asset_contact',)

class addInstitutionForm(forms.ModelForm):
    institution_name = forms.CharField(required=False, max_length=500)
    institution_details = forms.CharField(required=False, max_length=500)
    institution_address = forms.CharField(required=False, max_length=500)
    institution_contact = forms.CharField(required=False, max_length=500)

    class Meta:
        model = Institutions
        fields = ('institution_name','institution_details','institution_address','institution_contact',)
