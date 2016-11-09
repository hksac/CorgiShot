# -*- coding:utf-8 -*-
from django.contrib import admin
from ShotEngine.models import Corporator

from ShotEngine.models import ProjectBaseTemplate

from ShotEngine.models import TeamMember

from ShotEngine.models import Scene
from ShotEngine.models import ShotSets
from ShotEngine.models import ShotRepository

from ShotEngine.models import TaskRepository
from ShotEngine.models import CommentRepository
from ShotEngine.models import DepartmentRepository
from ShotEngine.models import StatusRepository

from django.contrib import admin
from django.utils.text import capfirst

from django.contrib.admin.options import TabularInline,StackedInline
from django.contrib.admin.utils import quote, unquote

from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
csrf_protect_m = method_decorator(csrf_protect)

from django.db import models, router, transaction
#from django.utils.datastructures import SortedDict



def find_model_index(name):
    count = 0
    contextlist = [
        'Groups',
        'Users',
        'Corporators',
        'Team members',
        'Department repositorys',
        'Project base templates',
        'Scenes',
        'Shot setss',
        'Shot repositorys',
        'Task repositorys',
        'Comment repositorys',
        'Status repositorys',
        ]
    count = contextlist.index(name)
    return count
       

def index_decorator(func):
    def inner(*args, **kwargs):
        templateresponse = func(*args, **kwargs)
        for app in templateresponse.context_data['app_list']:
            app['models'].sort(key=lambda x: find_model_index(x['name']))
        return templateresponse
    return inner


####################################################################################################
from ShotEngine.forms import TaskRepositoryForm,TaskRepositoryForm_MATTEPAINTNG,TaskRepositoryForm_ROTOPAINT
class TaskRepositoryAdmin(admin.ModelAdmin):
    list_display    = ('shot', 'department','artist','currentstatus','currentversion')
    list_filter     = ('department',)
    ordering        = ('-id', )
    search_fields   = ('shot', 'leader', 'artist' , )

    # shot              = models.ForeignKey('ShotRepository', related_name='tasklist',)
    # department        = models.ForeignKey('DepartmentRepository', blank=False,)
    # leader            = models.ForeignKey('Corporator',related_name='task_as_leader',)
    # artist            = models.ForeignKey('Corporator',related_name='task_as_artist',)
    # currentstatus     = models.ForeignKey('StatusRepository',)
    # currentversion    = models.IntegerField(default=0,)
    # assignTime        = models.DateTimeField(default=timezone.now, )




class TaskRepositoryInlineAdmin(TabularInline):
    model = TaskRepository 
    form = TaskRepositoryForm
    can_delete = True
    show_change_link = True
    can_add = True
    extra = 1
    can_order =True
    list_display = ('department','leader','artist',) 
    # def get_form(self, request, obj=None, **kwargs):
    #     print 'get_form.get_form.get_form.get_form.'
    #     super(TaskRepositoryInlineAdmin_MATTEPAINTNG,self).get_form(request, obj=None, **kwargs)


class TaskRepositoryInlineAdmin_MATTEPAINTNG(TaskRepositoryInlineAdmin):
    verbose_name = u"任务分支-MATTEPAINTNG"
    verbose_name_plural = u"任务分支-MATTEPAINTNG"
    def get_queryset(self, request):
        qs = self.model._default_manager.filter(department=1)
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


class TaskRepositoryInlineAdmin_ROTOPAINT(TaskRepositoryInlineAdmin):
    verbose_name = u"任务分支-ROTOPAINT"
    verbose_name_plural = u"任务分支-ROTOPAINT"
    def get_queryset(self, request):
        qs = self.model._default_manager.filter(department=2)
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


class TaskRepositoryInlineAdmin_MODEL(TaskRepositoryInlineAdmin):
    verbose_name = u"任务分支-MODEL"
    verbose_name_plural = u"任务分支-MODEL"
    def get_queryset(self, request):
        qs = self.model._default_manager.filter(department=3)
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        print qs
        #print request.method
        #print request.GET
        #print self.model.__dict__
        # print request.POST
        # if request.method == 'GET' and qs == []:
        #     self.model._default_manager.create(shot)
        return qs
    # @csrf_protect_m
    # @transaction.atomic
    # def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
    #     print 'changeform_view_MODEL'
    #     super(TaskRepositoryInlineAdmin_MODEL,self).changeform_view(request, object_id=None, form_url='', extra_context=None)


class TaskRepositoryInlineAdmin_MATCHMOVE(TaskRepositoryInlineAdmin):
    verbose_name = u"任务分支-MATCHMOVE"
    verbose_name_plural = u"任务分支-MATCHMOVE"
    def get_queryset(self, request):
        qs = self.model._default_manager.filter(department=4)
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


class TaskRepositoryInlineAdmin_EFFECTS(TaskRepositoryInlineAdmin):
    verbose_name = u"任务分支-EFFECTS"
    verbose_name_plural = u"任务分支-EFFECTS"
    def get_queryset(self, request):
        qs = self.model._default_manager.filter(department=5)
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


class TaskRepositoryInlineAdmin_LIGHTTING(TaskRepositoryInlineAdmin):
    verbose_name = u"任务分支-LIGHTTING"
    verbose_name_plural = u"任务分支-LIGHTTING"
    def get_queryset(self, request):
        qs = self.model._default_manager.filter(department=6)
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


class TaskRepositoryInlineAdmin_COMPOSITING(TaskRepositoryInlineAdmin):
    verbose_name = u"任务分支-COMPOSITING"
    verbose_name_plural = u"任务分支-COMPOSITING"
    def get_queryset(self, request):
        qs = self.model._default_manager.filter(department=7)
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs



####################################################################################################


class ShotRepositoryAdmin(admin.ModelAdmin):
    list_display    = ('shotName', 'sceneName',)
    list_filter     = ('sceneName','sceneName__projectName')
    ordering        = ('-id', )
    search_fields   = ('shotName', )
    inlines = [
        TaskRepositoryInlineAdmin_MATTEPAINTNG,
        TaskRepositoryInlineAdmin_ROTOPAINT,
        TaskRepositoryInlineAdmin_MODEL,
        TaskRepositoryInlineAdmin_MATCHMOVE,
        TaskRepositoryInlineAdmin_EFFECTS,
        TaskRepositoryInlineAdmin_LIGHTTING,
        TaskRepositoryInlineAdmin_COMPOSITING,
        ]

    from ShotEngine.forms import HiperShotRepositoryForm
    form            = HiperShotRepositoryForm

    def save_form(self, request, form, change):
        """
        Given a ModelForm return an unsaved instance. ``change`` is True if
        the object is being changed, and False if it's being added.
        """
        print 'save_form '
        print change
        # print request.POST
        return form.save(commit=False)

    def save_model(self,request,obj,form,change):
        print 'save_model '
        obj.save()

    def save_formset(self, request, form, formset, change):
        """
        Given an inline formset save it to the database.
        """
        print 'save_formset '
        print len(formset)
        print formset.total_form_count()
        print formset.initial_form_count()
        print change
        # from django.forms import modelformset_factory
        # from ShotEngine.forms import TaskRepositoryForm
        # TaskRepository_FormSet = modelformset_factory(TaskRepository,form=TaskRepositoryForm)
        # newformset = TaskRepository_FormSet(initial={'shot':form.instance.pk,'department':1})
        # newformset.save()
        # print formset.__class__,formset.total_form_count(),newformset.__class__,newformset.total_form_count()
        print '------------------------------------------------------------'
        formset.save()

    def save_related(self, request, form, formsets, change):
        print 'save_related '
        form.save_m2m()
        print 'formsets' , formsets
        for formset in formsets:
            self.save_formset(request, form, formset, change=change)


    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        print 'changelist_view'
        return super(ShotRepositoryAdmin,self).changelist_view(request, extra_context=None)

    @csrf_protect_m
    @transaction.atomic
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        print 'changeform_view'
        print request
        print object_id
        print form_url
        print extra_context
        return super(ShotRepositoryAdmin,self).changeform_view(request, object_id, form_url, extra_context)

            
####################################################################################################



class CommentRepositoryInlineAdmin(TabularInline):
    #from ShotEngine.forms import ShotRepositoryForm
    model = CommentRepository 
    #form = ShotRepositoryForm
    can_delete = False
    show_change_link = True
    extra = 0
    can_order =True
    verbose_name = u"评论"
    verbose_name_plural = u"评论"
    list_displays = ('content','submitTime',) 



####################################################################################################
#Designation a Scene Model.
class ShotRepositoryInlineAdmin(TabularInline):
    from ShotEngine.forms import ShotRepositoryForm
    model = ShotRepository 
    form = ShotRepositoryForm
    can_delete = False
    show_change_link = True
    extra = 0
    can_order =True
    verbose_name = u"镜头"
    verbose_name_plural = u"镜头"
    list_displays = ('sceneName','shotName','Description',) 



class SceneAdmin(admin.ModelAdmin):
    list_display = ('title','description','projectName')
    list_filter  = ('projectName',)
    inlines = [ShotRepositoryInlineAdmin]
    from ShotEngine.forms import SceneForm
    form          = SceneForm



class SceneInlineAdmin(TabularInline):
    model = Scene
    verbose_name = u"场次"
    verbose_name_plural = u"场次"
    can_delete = False
    show_change_link = True
    extra = 0
    can_order =True
    list_display    = ('title', 'description',)

    # def get_formset(self, request, obj=None, **kwargs):
    #     result = super(SceneInlineAdmin,self).get_formset(request, obj=None, **kwargs)
    #     return result
        


class ProjectBaseTemplateAdmin(admin.ModelAdmin):
    list_display  = ('ProjName', 'ProjRootPath', 'modifyTime',)
    list_filter   = ('Producer', 'SuperVisor',)
    ordering      = ('-ProjName', )
    search_fields = ('ProjName', 'ProjRootPath', 'modifyTime',)
    from ShotEngine.forms import ProjectBaseTemplateForm
    form          = ProjectBaseTemplateForm

    inlines = [SceneInlineAdmin]  





class TeamMemberAdmin(admin.ModelAdmin):
    list_display  = ('corporator','teamPosition','date_joined',)
    list_filter   = ('corporator','teamPosition',)
    ordering      = ('-date_joined',)
    search_fields = ('corporator','teamPosition','date_joined',)





class CorporatorAdmin(admin.ModelAdmin):
    list_display    = ('alias_name','username','email','last_login','job_title',)
    list_filter     = ('department','is_active',)
    ordering        = ('-date_joined',)
    search_fields   = ('username','alias_name','is_active',)
    readonly_fields = (
        'groups',
        'password',
        'user_permissions',
        'date_joined',
        'last_login',
        )

    def save_model(self,request,obj,form,change):
        if not change:
            raw_password = form.cleaned_data["password"]
            obj.set_password(raw_password)
        obj.save()



class StatusRepositoryAdmin(admin.ModelAdmin):
    list_display = ('statusName','statusAliase','submiter')
    from ShotEngine.forms import StatusRepositoryForm
    form         = StatusRepositoryForm
    readonly_fields = (
        'submiter',
        )
    def save_model(self,request,obj,form,change):
        if not change:
            obj.submiter = request.user
        obj.save()

####################################################################################################

# Register your models here.
admin.site.register(DepartmentRepository)
admin.site.register(Corporator, CorporatorAdmin)
admin.site.register(TeamMember, TeamMemberAdmin)
admin.site.register(ProjectBaseTemplate, ProjectBaseTemplateAdmin )


#This about shot setting.
admin.site.register(Scene, SceneAdmin )
admin.site.register(ShotSets )
admin.site.register(ShotRepository, ShotRepositoryAdmin )
admin.site.register(TaskRepository, TaskRepositoryAdmin )
admin.site.register(CommentRepository )
admin.site.register(StatusRepository, StatusRepositoryAdmin )


registry = {}
registry.update(admin.site._registry)

admin.site._registry = registry
admin.site.index     = index_decorator(admin.site.index)
admin.site.app_index = index_decorator(admin.site.app_index)