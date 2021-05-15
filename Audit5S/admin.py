from django.contrib import admin
from .models import *
from typing import Set

from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model


User = get_user_model()

class UserAdminCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('nom', 'email',) #'full_name',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserAdminChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ( 'email','nom', 'password', 'role')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

class UserAdmin(BaseUserAdmin):
    #when a non-superuser tries to edit a user, the username field will be disabled. Any attempt to modify the username through Django Admin will fail.
    #when a non-superuser tries to make himself  a superuser, the superuser field will be disabled. 
    #To manage permissions only using groups, you need to prevent users from granting permissions to specific users. Instead, you want to only allow associating users to groups

    #When obj is None, the form is used to create a new user.When obj is not None, the form is used to edit an existing user. 
    

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        disabled_fields=set()

        if not is_superuser:
            disabled_fields |={'username','is_superuser','user_permissions','groups'}
        # Prevent non-superusers from editing their own permissions
        #To check if the user making the request is operating on themselves, you compare request.user with obj. Because this is the user admin, obj is either an instance of User, or None. When the user making the request, request.user, is equal to obj, then it means that the user is updating themselves
        if (
            not is_superuser
            and obj is not None
            and obj == request.user
        ):
            disabled_fields |= {
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            } 
        for f in disabled_fields:
            if f in form.base_fields:
                form.base_fields[f].disabled = True    
            
        return form
    # The forms to add and change user instances
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('username','nom' , 'prenom' , 'numtel' ,'departement','role','groups')
    list_filter = ('admin', 'staff', 'role')
    
    search_fields = ('nom','prenom')
    ordering = ['prenom']
    fieldsets = (
        (None, {'fields': ('username','nom', 'prenom' , 'numtel' , 'photo','departement', 'password')}),)
         
    #add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
     #overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username','role','nom', 'prenom' , 'numtel' , 'photo','departement','email', 'password1', 'password2')}
        ),
    )


admin.site.register(User)
admin.site.register(Audit)
admin.site.register(PlanAction)
admin.site.register(Action)
admin.site.register(Standard)
admin.site.register(Categorie)
admin.site.register(Zone)
admin.site.register(Responsable)

