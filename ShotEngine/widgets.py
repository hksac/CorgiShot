# -*- coding:utf-8 -*-
from django import forms


class SubSelectWidget(forms.Select):
    class Media:
        #css = {"all": ("widgets.css", )}
        js = ('javascript/respond_to_root_path.js',)


class ShotSelectWidget(forms.Select):
    class Media:
        #css = {"all": ("widgets.css", )}
        js = ('javascript/respond_to_Project_Choice.js',)