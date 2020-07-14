from django import forms

from core.models import Like, User, Post


class LikeForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.all(), to_field_name='id')
    post = forms.ModelChoiceField(queryset=Post.objects.all(), to_field_name='id')
    
    class Meta:
        model = Like
        fields = ('user', 'post')
