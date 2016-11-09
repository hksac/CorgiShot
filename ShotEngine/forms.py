# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.contrib.auth import (
    authenticate, get_user_model, password_validation,
)
from django.contrib.auth.hashers import (
    UNUSABLE_PASSWORD_PREFIX, identify_hasher,
)
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.forms.utils import flatatt
from django.template import loader
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.html import format_html, format_html_join
from django.utils.http import urlsafe_base64_encode
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from django.utils.translation import ugettext, ugettext_lazy as _

from CorgiShot.settings import STORAGE_ROOT_PATH
from ShotEngine.widgets import SubSelectWidget,ShotSelectWidget

from ShotEngine.models import Corporator
from ShotEngine.models import TaskRepository
from ShotEngine.models import ShotRepository
from ShotEngine.models import ProjectBaseTemplate
from ShotEngine.models import Scene
from ShotEngine.models import DepartmentRepository
from ShotEngine.models import StatusRepository

import os

class AuthenticationGeneralUserForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """
    username = forms.CharField(max_length=254)
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)

    error_messages = {
        'invalid_login': _("Please enter a correct %(username)s and password. "
                           "Note that both fields may be case-sensitive."),
        'inactive': _("This account is inactive."),
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super(AuthenticationForm, self).__init__(*args, **kwargs)

        # Set the label for the "username" field.
        UserModel = get_user_model()
        self.username_field = UserModel._meta.get_field(UserModel.USERNAME_FIELD)
        if self.fields['username'].label is None:
            self.fields['username'].label = capfirst(self.username_field.verbose_name)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username,
                                           password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        """
        Controls whether the given User may log in. This is a policy setting,
        independent of end-user authentication. This default behavior is to
        allow login by active users, and reject login by inactive users.

        If the given user cannot log in, this method should raise a
        ``forms.ValidationError``.

        If the given user may log in, this method should return None.
        """
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache







class FolderPathField(forms.ChoiceField):
    def __init__(self, path, match=None, recursive=False, allow_files=False,
                 allow_folders=True, required=True, widget=SubSelectWidget, label=None,
                 initial=None, help_text='', *args, **kwargs):

        self.path, self.match, self.recursive = path, match, recursive

        self.allow_files, self.allow_folders = allow_files, allow_folders
        
        super(FolderPathField, self).__init__(
            choices=(), required=required, widget=widget, label=label,
            initial=initial, help_text=help_text, *args, **kwargs
        )

        if self.required:
            self.choices = []
        else:
            self.choices = [("", "---------")]

        if self.match is not None:
            self.match_re = re.compile(self.match)

        if recursive:
            for root, dirs, files in sorted(os.walk(self.path)):
                if self.allow_files:
                    for f in files:
                        f = f.decode('gbk')
                        if self.match is None or self.match_re.search(f):
                            f = os.path.join(root, f)
                            self.choices.append((f, f.replace(path, "", 1)))
                if self.allow_folders:
                    for f in dirs:
                        f = f.decode('gbk')
                        if f == '__pycache__':
                            continue
                        if self.match is None or self.match_re.search(f):
                            f = os.path.join(root, f)
                            self.choices.append((f, f.replace(path, "", 1)))
        else:
            try:
                for f in sorted(os.listdir(self.path)):
                    f = f.decode('gbk')
                    if f == '__pycache__':
                        continue
                    full_file = os.path.join(self.path, f)
                    if (((self.allow_files and os.path.isfile(full_file)) or
                            (self.allow_folders and os.path.isdir(full_file))) and
                            (self.match is None or self.match_re.search(f))):
                        self.choices.append((full_file, f))
            except OSError:
                pass

        self.widget.choices = self.choices



class ProjectBaseTemplateForm(forms.ModelForm):
    ProjName           = forms.CharField(
        max_length=40, 
        label=_(u'项目名称'),
        )
    ProjAliasName      = forms.CharField(
        max_length=40, 
        label=_(u'项目英文名称'),
        )
    ProjRootPath       = FolderPathField(
        path=STORAGE_ROOT_PATH, 
        widget = SubSelectWidget(
            attrs={
                'onchange':r"var temp = '" + STORAGE_ROOT_PATH.replace('\\','/') + "';adjustOptionForSubPath(temp);",
                },
        ),
        label=_(u'项目根目录'),
        allow_files=False, 
        allow_folders=True, 
        )

    Producer           = forms.ModelMultipleChoiceField(
        required=True,
        widget = forms.CheckboxSelectMultiple(),
        queryset = Corporator.objects.filter(job_title = 0),
        label=_(u'制片'),
        )
    SuperVisor         = forms.ModelMultipleChoiceField(
        required=True,
        widget = forms.CheckboxSelectMultiple(),
        queryset = Corporator.objects.filter(job_title = 4),
        label=_(u'视效总监'),
        )
    TeamLeader         = forms.ModelMultipleChoiceField(
        required=True,
        widget   = forms.CheckboxSelectMultiple(),
        queryset = Corporator.objects.filter(job_title = 2),
        label=_(u"组长"),
        )


    RawPlatesPath      = forms.CharField(
        widget = forms.TextInput(
            attrs={
                'style':'width:500px',
            }),
        label=_(u"原始素材路径"), 
        help_text=u'This Field is used for store orignal sequence path.',
        )
    AssetsPath         = forms.CharField(
        widget = forms.TextInput(
            attrs={
                'style':'width:500px',
            }),
        label=_(u"资产路径"), 
        help_text=u'This Field is used for store asserts path.',
        )
    VFXPath            = forms.CharField(
        widget = forms.TextInput(
            attrs={
                'style':'width:500px',
            }),
        label=_(u"制作路径"), 
        help_text=u'This Field is used for store work space path.',
        )
    DailyPath          = forms.CharField(
        widget = forms.TextInput(
            attrs={
                'style':'width:500px',
            }),
        label=_(u"Daily路径"), 
        help_text=u'This Field is used for store daily path.',
        )
    EditPath           = forms.CharField(
        widget = forms.TextInput(
            attrs={
                'style':'width:500px',
            }),
        label=_(u"剪辑路径"), 
        help_text=u'This Field is used for store editor space path.',
        )
    creatTime          = forms.DateTimeField(
        label=_(u"创建时间"),
        initial = timezone.now(),
        )
    modifyTime         = forms.DateTimeField(
        label=_(u"修改时间"),
        initial = timezone.now(),
        )
        
    def __init__(self, query_set=None, *args, **kwargs):
        if query_set != None:
            super(ProjectBaseTemplateForm, self).__init__(query_set, *args, **kwargs)
        else:
            if kwargs.get('instance'):
                super(ProjectBaseTemplateForm, self).__init__(query_set, *args, **kwargs)
                self.fields['creatTime'].initial   = timezone.now()
                self.fields['modifyTime'].initial  = timezone.now()
            else:
                super(ProjectBaseTemplateForm, self).__init__(query_set, *args, **kwargs)



class ShotRepositoryForm(forms.ModelForm):

    sceneName         = forms.ModelChoiceField(
        widget = ShotSelectWidget(
            attrs={
                'onchange':'getSuperVisorFromChoice();',
                },
        ),
        label=_(u"场次名称"), 
        queryset      = Scene.objects.all(),
        )
    shotName      = forms.CharField(
        label=_(u"镜头名称"), 
        )
    Description   = forms.CharField(
        label=_(u"镜头备注"), 
        )
    createTime   = forms.DateTimeField(
        disabled = True,
        label=_(u"创建时间"), 
        input_formats='%Y-%m-%d %H:%M',
        initial = timezone.now(),
    )
    PublishTime   = forms.DateTimeField(
        required = False,
        disabled = True,
        label=_(u"发布时间"), 
        input_formats='%Y-%m-%d %H:%M',
        initial  = timezone.now(),
        )

    class Meta:
        exclude = []




class HiperShotRepositoryForm(ShotRepositoryForm):
    projectName       = forms.CharField(
        required = False,
        disabled = True,
        initial = '',
        label=_(u"项目名称"), 
    )
    Supervisor        = forms.CharField(
        required = False,
        disabled = True,
        initial = '',
        label=_(u'视效总监'),
    )

    def __init__(self, query_set=None, *args, **kwargs):
        if query_set == None and kwargs.get('instance'):
            #Display the content of existent shot.
            super(HiperShotRepositoryForm, self).__init__(query_set, *args, **kwargs)
            scene   = kwargs['instance'].sceneName
            project = scene.projectName
            self.fields['projectName'].initial = unicode(project)  
            self.fields['Supervisor'].initial  = ','.join([unicode(proj) for proj in project.SuperVisor.all()])
        else:
            super(HiperShotRepositoryForm, self).__init__(query_set, *args, **kwargs)




class SceneForm(forms.ModelForm):

    projectName       = forms.ModelChoiceField(
        label=_(u"项目名称"), 
        queryset      = ProjectBaseTemplate.objects.all(),
        )
    title             = forms.CharField(label=_(u"场次名称"), )
    description       = forms.CharField(label=_(u"场次描述"), ) 
    Supervisor        = forms.CharField(
        required = False,
        disabled = True,
        initial = '',
        label=_(u'视效总监'),
    )
    def __init__(self, query_set=None, *args, **kwargs):
        #submit query data.
        if query_set != None:
            super(SceneForm, self).__init__(query_set, *args, **kwargs)
        else:
            #get model instance from database.
            if kwargs.get('instance'):
                super(SceneForm, self).__init__(query_set, *args, **kwargs)
                scene   = kwargs['instance']
                project = scene.projectName
                self.fields['Supervisor'].initial  = ','.join([unicode(proj) for proj in project.SuperVisor.all()])
            #add a new data record.
            else:
                super(SceneForm, self).__init__(query_set, *args, **kwargs)
    class Meta:
        ordering = []



###################################################################################################
class TaskRepositoryForm(forms.ModelForm):
    shot              = forms.ModelChoiceField(
        label=_(u"镜头名称"), 
        queryset      = ShotRepository.objects.all(),
        )
    department        = forms.ModelChoiceField(
        label=_(u"部门名称"), 
        queryset      = DepartmentRepository.objects.all(),
    )
    class Meta:
        model = TaskRepository
        exclude = []
    def __init__(self, query_set=None, *args, **kwargs):
        super(TaskRepositoryForm, self).__init__(*args, **kwargs)
        if query_set == None and not kwargs.get('instance'):
            self.fields['department'].initial  = 2

        


class TaskRepositoryForm_MATTEPAINTNG(TaskRepositoryForm):
    def __init__(self, query_set=None, *args, **kwargs):
        super(TaskRepositoryForm_MATTEPAINTNG, self).__init__(*args, **kwargs)
        self.fields['department'].initial  = 1



class TaskRepositoryForm_ROTOPAINT(TaskRepositoryForm):
    def __init__(self, query_set=None, *args, **kwargs):
        super(TaskRepositoryForm_ROTOPAINT, self).__init__(*args, **kwargs)
        self.fields['department'].initial  = 2
        #if query_set == None:
        # if query_set == None and kwargs.get('instance'):
        #     super(TaskRepositoryForm_ROTOPAINT, self).__init__(query_set, *args, **kwargs)
        #     self.fields['department'].initial  = u'ROTOPAINT'
        # else:
        #     super(TaskRepositoryForm_ROTOPAINT, self).__init__(query_set, *args, **kwargs)
        #     self.fields['department'].initial  = u'ROTOPAINT'



class StatusRepositoryForm(forms.ModelForm):
    submiter = forms.CharField(max_length=20)
#     def __init__(self, query_set=None, *args, **kwargs):
#         if query_set == None and not kwargs.get('instance'):
#             super(StatusRepositoryForm, self).__init__(query_set, *args, **kwargs)
#             # self.fields['submiter'].initial  = u''
#         else:
#             super(StatusRepositoryForm, self).__init__(query_set, *args, **kwargs)
#     class Meta:
#         model = StatusRepository 
#         exclude = []



u'MATTEPAINTNG'
u'ROTOPAINT'
u'MODEL'
u'MATCHMOVE'
u'EFFECTS'
u'LIGHTTING'
u'COMPOSITING'
u'PRODUCER'
u'SUPERVISOR'

""""
None () 
{
    u'auto_id': u'id_%s', 
    u'files': {}, 
    u'error_class': <class 'django.forms.utils.ErrorList'>, 
    u'empty_permitted': True, 
    u'prefix': u'tasklist-0', 
    u'data': <QueryDict: 
    {
        u'tasklist-2-0-assignTime_0': [u'2016-11-04'], 
        u'tasklist-2-0-assignTime_1': [u'17:39:59'], 
        u'tasklist-__prefix__-id': [u''],
        u'tasklist-__prefix__-assignTime_1': [u'17:39:59'], 
        u'tasklist-2-MAX_NUM_FORMS': [u'1000'], 
        u'initial-tasklist-2-__prefix__-assignTime_1': [u'17:39:59'], 
        u'tasklist-2-__prefix__-department': [u'ROTOPAINT'], 
        u'tasklist-0-assignTime_1': [u'17:39:59'], 
        u'tasklist-0-assignTime_0': [u'2016-11-04'], 
        u'tasklist-2-__prefix__-currentversion': [u'0'], 
        u'tasklist-__prefix__-leader': [u''], 
        u'tasklist-__prefix__-assignTime_0': [u'2016-11-04'], 
        u'tasklist-0-currentstatus': [u''], 
        u'tasklist-2-TOTAL_FORMS': [u'1'], 
        u'tasklist-2-0-id': [u''], 
        u'_save': [u'Save'], 
        u'tasklist-2-__prefix__-assignTime_1': [u'17:39:59'], 
        u'Description': [u'dddd'], 
        u'tasklist-0-id': [u''], 
        u'tasklist-0-currentversion': [u'0'], 
        u'tasklist-0-department': [u'MATTEPAINTNG'], 
        u'tasklist-0-leader': [u'1'], 
        u'tasklist-2-0-leader': [u'4'], 
        u'tasklist-2-__prefix__-artist': [u''], 
        u'initial-tasklist-0-assignTime_0': [u'2016-11-04'], 
        u'initial-tasklist-0-assignTime_1': [u'17:39:59'], 
        u'tasklist-0-artist': [u'5'], 
        u'tasklist-2-__prefix__-leader': [u''], 
        u'shotName': [u'MBB_E_0010'], 
        u'initial-tasklist-__prefix__-assignTime_1': [u'17:39:59'], 
        u'initial-tasklist-__prefix__-assignTime_0': [u'2016-11-04'], 
        u'csrfmiddlewaretoken': [u'IY207CO5OWScIbdN8E8z5sUfxgl4RMtR'], 
        u'tasklist-MAX_NUM_FORMS': [u'1000'], 
        u'tasklist-0-shot': [u'1'], 
        u'tasklist-2-0-department': [u'ROTOPAINT'], 
        u'tasklist-2-INITIAL_FORMS': [u'0'], 
        u'tasklist-MIN_NUM_FORMS': [u'0'], 
        u'tasklist-2-0-artist': [u'7'], 
        u'tasklist-__prefix__-department': [u'MATTEPAINTNG'], 
        u'tasklist-__prefix__-currentversion': [u'0'], 
        u'tasklist-2-__prefix__-assignTime_0': [u'2016-11-04'], 
        u'tasklist-__prefix__-shot': [u'1'], 
        u'initial-tasklist-2-0-assignTime_1': [u'17:39:59'], 
        u'initial-tasklist-2-0-assignTime_0': [u'2016-11-04'], 
        u'initial-tasklist-2-__prefix__-assignTime_0': [u'2016-11-04'], 
        u'tasklist-2-__prefix__-shot': [u'1'], 
        u'tasklist-TOTAL_FORMS': [u'1'], 
        u'sceneName': [u'1'], 
        u'tasklist-2-MIN_NUM_FORMS': [u'0'], 
        u'tasklist-2-0-currentstatus': [u''], 
        u'tasklist-2-__prefix__-id': [u''], 
        u'tasklist-2-__prefix__-currentstatus': [u''], 
        u'tasklist-INITIAL_FORMS': [u'0'], 
        u'tasklist-2-0-shot': [u'1'], 
        u'tasklist-__prefix__-artist': [u''], 
        u'tasklist-2-0-currentversion': [u'0'], 
        u'tasklist-__prefix__-currentstatus': [u'']
    }>
}
"""