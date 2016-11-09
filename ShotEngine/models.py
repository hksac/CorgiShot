# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db import models

# Create your models here.
from django.contrib import auth
from django.contrib import admin
from django.contrib.auth.models import _user_get_all_permissions
from django.contrib.auth.models import _user_has_perm
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import Permission
from django.contrib.auth.models import Group
from django.contrib.auth.hashers import (
    check_password, is_password_usable, make_password,
)
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.core import validators
from django.core.mail import send_mail
from CorgiShot.settings import STORAGE_ROOT_PATH

from django import forms

from django.contrib.auth import password_validation
from django.contrib.auth.hashers import (
    check_password, is_password_usable, make_password,
)


#from django.contrib.auth.models import _user_has_module_perms
JobTitleList = (
    (0,u'Producer'),
    (1,u'Coordinator'),
    (2,u'Team Leader'),
    (3,u'Sub Team Leader'),
    (4,u'Supervisor'),
    (5,u'Artist'),
    (6,u'TD'),
    )


####################################################################################################
####################################################################################################
############################# DEFINE ## Department ## Repository ## MODEL ##########################
############################# DEFINE ## Department ## Repository ## MODEL ##########################
####################################################################################################
####################################################################################################

#In initial_data.json file you need plus one number.
class DepartmentRepository(models.Model):
    choiceList = (
        (0,u'MATTEPAINTNG'),
        (1,u'ROTOPAINT'),
        (2,u'MODEL'),
        (3,u'MATCHMOVE'),
        (4,u'EFFECTS'),
        (5,u'LIGHTTING'),
        (6,u'COMPOSITING'),
        (7,u'PRODUCER'),
        (8,u'SUPERVISOR'),
        )
    departmentName    = models.IntegerField(default=0, choices=choiceList, blank=True,)
    # class Meta:
    #     verbose_name_plural = u'部门'
    #     verbose_name        = u'部门'
    def __unicode__(self):
        return unicode(self.get_departmentName_display())
    



####################################################################################################
####################################################################################################
############################### This models defined tree main class ################################
################# @Corporator@ ##### @CorporatorPERMISSION@ ##### @CorporatorGROUP@ ################
######################  Combine these tree models to a Anthencatition System!  #####################
####################################################################################################
####################################################################################################

class CorporatorPermissionsMixin(models.Model):
    """
    A mixin class that adds the fields and methods necessary to support
    Django's Group and Permission model using the ModelBackend.
    """
    is_superuser = models.BooleanField(
        _('superuser status'),
        default  = False,
        help_text=_(
            'Designates that this user has all permissions without '
            'explicitly assigning them.'
        ),
    )
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('corporatorgroups'),
        blank=True,
        help_text=_(
            'The corporatorgroups this corporator belongs to. A corporator will get all corporatorpermissions '
            'granted to each of their groups.'
        ),
        related_name      ="corporator_set",
        related_query_name="corporatoruser",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name =_('corporator permissions'),
        blank        =True,
        help_text=_('Specific permissions for this corporator.'),
        related_name ="corporator_set",
        related_query_name="corporatoruser",
    )

    class Meta:
        abstract = True

    def get_group_permissions(self, obj=None):
        """
        Returns a list of permission strings that this user has through their
        groups. This method queries all available auth backends. If an object
        is passed in, only permissions matching this object are returned.
        """
        permissions = set()
        for backend in auth.get_backends():
            if hasattr(backend, "get_group_permissions"):
                permissions.update(backend.get_group_permissions(self, obj))
        return permissions

    def get_all_permissions(self, obj=None):
        return _user_get_all_permissions(self, obj)

    def has_perm(self, perm, obj=None):
        """
        Returns True if the user has the specified permission. This method
        queries all available auth backends, but returns immediately if any
        backend returns True. Thus, a user who has permission from a single
        auth backend is assumed to have permission in general. If an object is
        provided, permissions for this specific object are checked.
        """

        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        # Otherwise we need to check the backends.
        return _user_has_perm(self, perm, obj)

    def has_perms(self, perm_list, obj=None):
        """
        Returns True if the user has each of the specified permissions. If
        object is passed, it checks if the user has all required perms for this
        object.
        """
        for perm in perm_list:
            if not self.has_perm(perm, obj):
                return False
        return True

    def has_module_perms(self, app_label):
        """
        Returns True if the user has any permissions in the given app label.
        Uses pretty much the same logic as has_perm, above.
        """
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True
        return _corporator_has_module_perms(self, app_label)



# A few helper functions for common logic between User and AnonymousUser.
def _user_get_all_permissions(user, obj):
    permissions = set()
    for backend in auth.get_backends():
        if hasattr(backend, "get_all_permissions"):
            try:
                print 'Successful updating permissions!',backend
                permissions.update(backend.get_all_permissions(user, obj))
            except:
                continue
    return permissions



#This function is used for check if this user has given inner function!
def _user_has_perm(user, perm, obj):
    """
    A backend can raise `PermissionDenied` to short-circuit permission checking.
    """
    for backend in auth.get_backends()[1:]:
        if not hasattr(backend, 'has_perm'):
            continue
        try:
            if backend.has_perm(user, perm, obj):
                return True
        except PermissionDenied:
            return False
    return False



def _corporator_has_module_perms(user, app_label):
    """
    A backend can raise `PermissionDenied` to short-circuit permission checking.
    """
    for backend in auth.get_backends()[1:]:
        if not hasattr(backend, 'has_module_perms'):
            continue
        try:
            if backend.has_module_perms(user, app_label):

                return True
        except PermissionDenied:
            return False
    return False



####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################

class CorporatorManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_artist(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('job_title', 5)
        return self._create_user(username, email, password, **extra_fields)



class Corporator(AbstractBaseUser, CorporatorPermissionsMixin):
    """rewrite a new user model,wish it has a good show."""
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Username and password are required. Other fields are optional.
    """
    #username is your login id.
    username = models.CharField(
        _('username'),
        max_length=30,
        unique    =True,
        help_text =_('Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[
            validators.RegexValidator(
                r'^[\w.@_]+$',
                _('Enter a valid username. This value may contain only '
                  'letters, numbers ' 'and @/. characters.')
            ),
        ],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    
    #first_name and last_name make up your real full name.
    alias_name = models.CharField(
        _('alias name'), 
        max_length=30, 
        blank=True,
        validators=[
            validators.RegexValidator(
                r'^[^%!@$#^&*()-=+<>?,/\\\[\]\'\":;{}]+$',
                _('Enter a valid alias name. This value may contain only '
                  'letters, numbers ' 'and @/. characters.')
            ),
        ])
        
    #This is your email address to receive and send email.
    email      = models.EmailField(_('email address'), blank=True)
    
    #is_active present this id's status.
    is_active  = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=True,
        help_text=_('Designates whether the user can log into this admin site.'),
    )

    #Make sure that one employee must and only have one title.
    #Through get_jobtitle_display() to get alias name.
    #Make this field dynamic.
    job_title   = models.IntegerField(
        choices = JobTitleList,
        default = 5,
        blank = False,
        )
    #job_title  = models.ForeignKey('JobTitle',blank=True,)
    
    department = models.ForeignKey('DepartmentRepository', blank=True,)

    #This is create time.
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now , )

    objects = CorporatorManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']


    class Meta:
        verbose_name = _('Corporator')
        verbose_name_plural = _('Corporators')


    def __unicode__(self):
        return unicode(self.alias_name)

    def get_full_name(self):
        return self.alias_name

    def get_short_name(self):
        return self.alias_name

    def get_alias_name(self):
        "Returns the alias name for the user."
        return self.alias_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self._password = raw_password

    def check_password(self, raw_password):
        """
        Return a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """
        def setter(raw_password):
            self.set_password(raw_password)
            # Password hash upgrades shouldn't be considered password changes.
            self._password = None
            self.save(update_fields=["password"])
        return check_password(raw_password, self.password, setter)
    
    def save(self, *args, **kwargs):
        super(Corporator, self).save(*args, **kwargs)
        if self._password is not None:
            password_validation.password_changed(self._password, self)
            self._password = None




####################################################################################################
####################################################################################################
############################# DEFINE ## SHOT ## SETS ## MODEL ######################################
############################# DEFINE ## SHOT ## SETS ## MODEL ######################################
####################################################################################################
####################################################################################################
class StatusRepository(models.Model):
    statusName        = models.CharField(max_length=40,unique=True,)
    statusAliase      = models.CharField(max_length=40,default='')
    submiter          = models.ForeignKey('Corporator')
    def __unicode__(self):
        return unicode(self.statusName)




#A Table Restore Comment Data.
class CommentRepository(models.Model):
    content           = models.CharField(max_length=100,)
    submitTime        = models.DateTimeField(default=timezone.now, )
    task              = models.ForeignKey('TaskRepository' , related_name='commentlist',)
    submitter         = models.ForeignKey('Corporator' ,related_name='Comments',)
    
    def __unicode__(self):
        return unicode(self.content)




#Define a Submitter to support a public share models to CommentRepository and TaskRepository.
class AbstractSubmitter(Corporator):
    submitter = models.ForeignKey('Corporator',related_name='as_submitters',)
    def __unicode__(self):
        return unicode(self.submitter)




#A Table Restore Sub Task Data.
class TaskRepository(models.Model):
    shot              = models.ForeignKey('ShotRepository', related_name='tasklist',)
    department        = models.ForeignKey('DepartmentRepository', blank=False,)
    leader            = models.ForeignKey('Corporator',related_name='task_as_leader', blank=True,)
    artist            = models.ForeignKey('Corporator',related_name='task_as_artist',blank=True,)
    currentstatus     = models.ForeignKey('StatusRepository',)
    currentversion    = models.IntegerField(default=0,)
    assignTime        = models.DateTimeField(default=timezone.now, )
    def __unicode__(self):
        return unicode(self.shot) + '__' + unicode(self.department)




####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
#A Table Restore Single Shot Data.
class ShotRepository(models.Model):
    sceneName         = models.ForeignKey('Scene'              , related_name='shotlist',)
    shotName          = models.CharField(max_length=40, blank=False,)
    Description       = models.CharField(max_length=100,blank=True,)
    createTime        = models.DateTimeField(default=timezone.now, )
    #PublishTime is finish time.
    PublishTime       = models.DateTimeField(blank=True )

    def __unicode__(self):
        return unicode(self.shotName)


class TeamMember(models.Model):
    corporator   = models.ForeignKey('Corporator')

    teamPosition = models.IntegerField(
        choices  = JobTitleList,
        default  = 5,
        blank    = False,
        )

    date_joined  = models.DateTimeField(_('date joined'), default=timezone.now, )




####################################################################################################
#Designation a Scene Model.
class Scene(models.Model):
    projectName       = models.ForeignKey('ProjectBaseTemplate', related_name=u'scenelist',)
    title             = models.CharField(max_length=40,)
    description       = models.CharField(max_length=100,)     
    def __unicode__(self):
        return unicode(self.title)



        
####################################################################################################
####################################################################################################
############################# DEFINE ## PROJECT ## MODEL ###########################################
############################# DEFINE ## PROJECT ## MODEL ###########################################
####################################################################################################
####################################################################################################

class ProjectBaseTemplate(models.Model):
    ProjName           = models.CharField(max_length=40, blank=True)
    ProjAliasName      = models.CharField(max_length=40, blank=True)
    ProjRootPath       = models.FilePathField(path=STORAGE_ROOT_PATH, )
    
    Producer           = models.ManyToManyField(
        Corporator,
        related_name=u'Project_Producers',
        limit_choices_to={'job_title':0},
        # blank=True,
        )
    SuperVisor         = models.ManyToManyField(
        Corporator,
        related_name=u'Project_Supervisors',
        limit_choices_to={'job_title':4},
        # blank=True,
        )
    TeamLeader         = models.ManyToManyField(
        Corporator,
        related_name=u'Project_Teamleaders',
        limit_choices_to={'job_title':3},
        # blank=True,
        )

    RawPlatesPath      = models.FilePathField(path=u'', )
    AssetsPath         = models.FilePathField(path=u'', )
    VFXPath            = models.FilePathField(path=u'', )
    DailyPath          = models.FilePathField(path=u'', )
    EditPath           = models.FilePathField(path=u'', )

    creatTime          = models.DateTimeField(default=timezone.now, )
    modifyTime         = models.DateTimeField(default=timezone.now, )
    def __unicode__(self):
        return unicode(self.ProjName)

    def save(self,*args,**kwargs):
        self.modifyTime = timezone.now()
        super(ProjectBaseTemplate,self).save(*args,**kwargs)




####################################################################################################



#A Designation Of Shot Set.
class ShotSets(models.Model):
    title             = models.CharField(max_length=40,blank=False,default=u'Shot Group')
    shotgroup = models.ManyToManyField(
        ShotRepository,
        related_name='ShotGroups',
        blank=True,
    )
    def __unicode__(self):
        return unicode(self.title)