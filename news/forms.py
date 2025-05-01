from django import forms
from .models import Article, Category, Tag

class ArticleForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        required=False
    )
    
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        required=False
    )
    
    class Meta:
        model = Article
        fields = [
            'title',
            'excerpt',
            'content',
            'featured_image',
            'categories',
            'tags',
            'status'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'excerpt': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'featured_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'data-max-size': '50',
                'onchange': 'validateImageSize(this)'
            }),
            'status': forms.Select(attrs={'class': 'form-select'})
        }

    class Media:
        js = ('js/image-validation.js',)

    def clean_featured_image(self):
        image = self.cleaned_data.get('featured_image')
        if image:
            if image.size > 50 * 1024:
                raise forms.ValidationError("Maximum file size allowed is 50KB")
        return image