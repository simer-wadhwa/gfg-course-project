import json
from django.shortcuts import render
from django.http import JsonResponse,HttpResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers import serialize
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from todo.choices import StatusChoices
from todo.models import Task
from todo.helper import update_obj


User = get_user_model()


# Create your views here.
@csrf_exempt
def register(request):
    if request.method != 'POST':
        return JsonResponse({
            "status" :"error",
            "message" : "Not Found",
            "payload" : {}
        }, status=404)
             
    
    request_data = json.loads(request.body)

    username = request_data.get('username',None)
    password = request_data.get('password', None)
    email = request_data.get('email',None)

    if username is None or password is None or email is None:
        return JsonResponse({
            "status" : "error",
            "message" :"Please provide enough Info",
            "payload" : {}

        }, status = 400)
    
    existing_user = User.objects.filter(username=username)

    if existing_user.exists():
        return JsonResponse({
            "status" : "error",
            "message" :"User Alread Exists",
            "payload" : {}
        }, status = 404)
    user = User(
        email = email,
        username = username
    )
    user.set_password(raw_password=password)
    user.save()
    return JsonResponse({
        "status" : "sucess",
        "message":"Successfully Registered",
        "payload" : {
            "email" : user.email,
            "username" : user.username
              }
    }, status=201)

@csrf_exempt
def login(request):
    if request.method != 'POST':
        return JsonResponse({
            "status" : "error",
            "message" : "Not Found",
            "payload" : {}

        }, status=404)

    request_data = json.loads(request.body)

    username = request_data.get("username",None)
    password = request_data.get("password",None)

    user = authenticate(username=username, password=password)

    if user is not None:
        django_login(request,user)
        return JsonResponse({
            "status" : "success",
            "message" : "Successfully Login",
            "payload" : {}
        }, status=200)
    else:
        return JsonResponse({
            "status" : "error",
            "message" : "Not Found",
            "payload" : {}

        }, status=404)

@login_required
def logout(request):
    if request.method != 'POST':
        return JsonResponse({
            "status" : "error",
            "message" : "Not Found",
            "payload" : {}

        }, status=404)
    
    django_logout(request)
    return JsonResponse({
            "status" : "success",
            "message" : "Successfully Logout",
            "payload" : {}
        }, status=200)
    
    
@login_required
def list_create_task(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user = request.user
        title = data["title"]
        description = data.get("description", "")
        status = data.get("status",StatusChoices.PENDING)

        task = Task.objects.create(
            user = user,
            title = title,
            description = description,
            status = status
        )

        task_serialized = serialize("json",[task],fields =('title','description','status','created_at','updated_at'))

        return JsonResponse({
            "status" : "success",
            "message" : "Successfully created",
            "payload" : json.loads(task_serialized)[0]
        }, status=200)
    if request.method == 'GET':
        
        page = request.GET.get("page",1)
        search =  request.GET.get("serach",None)
        status =  request.GET.get("status",None)
        ordering =  request.GET.get("ordering","-created_at")
        task_queryset = Task.objects.filter(user = request.user).order_by(ordering)
        #search
        if search is not None:
            task_queryset = task_queryset.filter(title__icontains=search)
        
        if status is not None:
            task_queryset = task_queryset.filter(status=status)
        

        #pagination
        page_size = 4
        paginator = Paginator(task_queryset,page_size)


        try:
         page_obj=paginator.page(page)
        
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        
        #previous

        if page_obj.has_previous():
            previous = page_obj.previous_page_number()
        else:
            previous=""

        #next

        if page_obj.has_next():
            next = page_obj.next_page_number()
        else:
            next = ""


        response_payload_results = serialize("json",page_obj.object_list)
        return JsonResponse({
            "status" : "success",
            "message" : "Successfully retrived",
            "payload" : {
                "count": page_obj.paginator.count, 
                "previous" : previous,
                "next" :next,
                "results": json.loads(response_payload_results)
                }
        }, status=200)
    else :
         return JsonResponse({
            "status" : "error",
            "message" : "Not Found",
            "payload" : {}

        }, status=404)

@login_required
def retrieve_update_task(request,id):
    if request.method == 'GET':
        task = Task.objects.filter(user=request.user,id=id).first()
        if task is None:
            response_data = {
                "status": "error",
                "message": "Task with this id not found",
                "payload": "{}"
            }
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        task_serialized = serialize("json",[task],fields = ('title', 'description','status','created_at','updated_at'))
        return JsonResponse({
            "status": "success",
            "message": "Successfully retrieved",
            "payload": json.loads(task_serialized)[0]
        }, status=200)
    

    if request.method in ["PUT", "PATCH"]:
        data = json.loads(request.body)
        task = Task.objects.filter(user=request.user, id=id).first()
        if task is None:
            return JsonResponse({
                "status": "error",
                "message": f"Task with {id} id not found",
                "payload": {}
            }, status=404)
        update_obj(task, **data)
        task_serialized = serialize("json", [task])
        return JsonResponse({
            "status": "success",
            "message": "Successfully updated",
            "payload": json.loads(task_serialized)[0]
        }, status=200)


    if request.method == "DELETE":
         
            task = Task.objects.filter(user=request.user, id=id).first()
            if task is None:
                return JsonResponse({
                    "status": "error",
                    "message": f"Task with {id} id not found",
                    "payload": {}
                }, status=404)
            
            task.delete()

            return JsonResponse({
            "status": "success",
            "message": "Successfully updated",
            "payload": {}
        }, status=200)
        
    
    



        
    