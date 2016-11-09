# -*- coding:utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse

from ShotEngine.models import ProjectBaseTemplate
from django.contrib.auth.models import Permission
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from ShotEngine.models import Corporator,Scene
# Create your views here.


def responseTest(request):
	try:
		username = request.user.username + " + " + request.user.alias_name 
	except:
		username = request.user.username + " + " + request.user.get_username()

	templateStr = 'User Information:<br><br>'
	templateStr += "User is:      " + request.user.__unicode__() + '<br>'
	templateStr += "UserID is:    " + unicode(request.user.pk) + '<br>'
	templateStr += "Groups is:    " + unicode(request.user.groups.all()) + '<br>'
	templateStr += "Permissions is:" + unicode(request.user.user_permissions.all()) + '<br>'
	templateStr += "UserName is:   " + username + '<br>'
	templateStr += "Session is:    " + unicode(request.session.__dict__) + '<br>'
	templateStr += "Host is:       " + request.get_host() + '<br>'
	templateStr += "Path is:       " + request.path + '<br>'
	templateStr += "Secure is:     " + unicode(request.is_secure()) + '<br>'
	templateStr += "Hellen Information:" + unicode(Corporator.objects.first().__dict__) + '<br>'
	templateStr += "Get_all_permissions() is:" + unicode(request.user.get_all_permissions()) + '<br><br>'
	templateStr += "All Group is:  "    + unicode(Group.objects.all()) + '<br><br>'
	templateStr += "All Permissions is" + unicode('<br>'.join([perm.__unicode__() for perm in Permission.objects.all()])) + "<br>"
	
	return HttpResponse(templateStr)


#built a list of sub path.
def return_SubPath_List(request,selectedRootPath):
    CurrentRoot = selectedRootPath
    RawPlatesPath      = CurrentRoot + '/VFX/rawPlates'
    AssetsPath         = CurrentRoot + '/VFX/assets'
    VFXPath            = CurrentRoot + '/VFX/sequences'
    DailyPath          = CurrentRoot + '/VFX/VFX_Dailies'
    EditPath           = CurrentRoot + '/Online'
    usersJson = [{
		'RawPlatesPath':RawPlatesPath,
		'AssetsPath':AssetsPath,
		'VFXPath':VFXPath,
		'DailyPath':DailyPath,
		'EditPath':EditPath,
		},]
    response = JsonResponse(usersJson , safe=False)
    return response


#return a list of supervisor in specialise project.
def return_project_Supervisor(request,sceneName):
    scenes      = Scene.objects.filter(pk=sceneName)[0]
    project = scenes.projectName
    SuperVisors = project.SuperVisor.all()
    supervisorJson = []
    SuperVisorName = ','.join([supvisor.alias_name for supvisor in SuperVisors])
    supervisorJson.append({"supervisor":SuperVisorName,"projname":project.__unicode__()})
    response = JsonResponse(supervisorJson,safe=False)
    return response