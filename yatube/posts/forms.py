from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from .models import Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')
        labels = {
            'text': _('text'),
            'group': _('group'),
        }
        help_texts = {
            'group': _('Необязательно к заполнению'),
        }

