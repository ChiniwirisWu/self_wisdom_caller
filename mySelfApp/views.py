from django.shortcuts import render
from django.db.models import F
from .models import Sentence

# Create your views here.

def main_view(request):
    s = Sentence.objects.all()[0]
    percentage = s.get_movement_percentage()
    return render(request,'main_view.html',{'percentage': percentage})

def observation_view(request):
    return render(request,'chat_view.html',{'title': 'observation', 'form_path': '/add_observation/', 'message': 'Please insert a new observation'})

def situation_view(request):
    return render(request,'chat_view.html',{'title':'situation', 'form_path': '/get_observation/', 'message': 'Please insert a situation'})

def stats_view_activities(request):
    s = Sentence.objects.all()[0]
    data = s.get_stats_data()
    return render(request,'stats_view.html',{'page_path':'/stats_Activities/' ,'title': 'stats', 'user': 'Orange Gat', 'labels' : data.keys(), 'logs': data['Activities'], 'category_selected': 'Activities'})

def stats_view_objects(request):
    s = Sentence.objects.all()[0]
    data = s.get_stats_data()
    return render(request,'stats_view.html',{'page_path':'/stats_Objects/' ,'title': 'stats', 'user': 'Orange Gat', 'labels' : data.keys(), 'logs': data['Objects'], 'category_selected': 'Objects'})

def stats_view_contexts(request):
    s = Sentence.objects.all()[0]
    data = s.get_stats_data()
    return render(request,'stats_view.html',{'page_path':'/stats_Contexts/' ,'title': 'stats', 'user': 'Orange Gat', 'labels' : data.keys(), 'logs': data['Contexts'], 'category_selected': 'Contexts'})

def stats_view_emotional_bridge(request):
    s = Sentence.objects.all()[0]
    data = s.get_stats_data()
    return render(request,'stats_view.html',{'page_path':'/stats_Bridges/' ,'title': 'stats', 'user': 'Orange Gat', 'labels' : data.keys(), 'logs': data['Bridges'], 'category_selected': 'Bridges'})

#functionalities
def add_observation(request):
    #pass via post
    if(request.POST['chatbar-message'] != ''):
        s = Sentence(text=str(request.POST['chatbar-message']))
        s.analyzeSentence()
    return render(request, 'chat_view.html', {'title': 'observation', 'message': 'Please insert a new observation'})

def remove_log(request, log_id, target):
    print(log_id, target)
    s = Sentence.objects.all()[0]
    data = s.get_stats_data()
    sentences = Sentence.objects.filter(target=target)
    s = sentences.get(pk=int(log_id))
    s.delete()
    return stats_view_emotional_bridge(request)



def get_observation(request):
    query = request.POST['chatbar-message']
    if(query != ''):
        response, message = Sentence().user_response(query)
        print(response['text'])
        return render(request, 'situation_response.html', {'user_response': response['text'], 'user_query': query, 'message': message , 'id': response['id'], 'form_path':'/get_choice/' })

def get_choice(request):
    query = request.POST['decision'] #"yes" || "no"
    sentence = Sentence.objects.get(pk=request.POST['id'])
    prev_percentage = round(sentence.get_movement_percentage())
    if(query =='yes'):
        sentence.action += 1
        sentence.save()
    else:
        sentence.unaction += 1
        sentence.save()
    new_percentage = round(sentence.get_movement_percentage())
    movement = new_percentage - prev_percentage
    return render(request, 'choice_view.html', {'movement': movement, 'form_path': '/situation/', 'percentage': new_percentage})
