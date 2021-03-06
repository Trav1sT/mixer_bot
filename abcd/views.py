from datetime import date
import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from abcd.models import *
from abcd.forms import *
from django.http.request import HttpRequest
from django.shortcuts import render
# Create your views here.


# Homepage before login
@login_required(login_url='/login')
def step1(request: HttpRequest):
    form = addCommunityForm(request.POST or None)
    if request.method == "POST":
        if not form.is_valid():
            print("invalid")
        else:
            addr = form.cleaned_data['community_addr']
            temp = Community(name=addr, owner=request.user, location=addr)
            temp.save()
    return render(request=request, template_name="abcd/step1.html",
                context={"form": form})

@login_required(login_url='/login')
def step2(request: HttpRequest):

    err = ""
    if request.method == "POST":
        dataDict = json.loads(request.body)
        print(dataDict)
        
        stake_name = dataDict["name"]
        stake = Stakeholders(name=stake_name, owner=request.user)
        stake.save()

        profile = Profile.objects.get(id=request.user.id)
        assocsString = profile.assocs
        if not assocsString:
            assocsString = "[]"

        strength_name = dataDict["strengths"]
        for x in strength_name:
            strength = Strengths(name=x, owner=request.user)
            strength.save()
            assocsString = appendToStringList(
                assocsString, 
                createConnString(stake_name, x)
            )
        
        interests_name = dataDict["interests"]
        for x in interests_name:
            interest = Interests(name=x, owner=request.user)
            interest.save()
            assocsString = appendToStringList(
                assocsString, 
                createConnString(stake_name, x)
            )
        
        qualities_name = dataDict["qualities"]
        for x in qualities_name:
            quality = Qualities(name=x, owner=request.user)
            quality.save()
            assocsString = appendToStringList(
                assocsString, 
                createConnString(stake_name, x)
            )
        
        profile.assocs = assocsString
        profile.save()

        print("Success")
        print(assocsString)

    stakeholders = Stakeholders.objects.filter(owner=request.user)
    return render(request=request, template_name="abcd/step2.html",
                  context={"individuals": stakeholders})



@login_required(login_url='/login')
def step3(request: HttpRequest):
    form = addAssetForm(request.POST or None)
    if request.method == "POST":
        print(request.user)
        if not form.is_valid():
            print("invalid")
        else:
            name = form.cleaned_data['asset_name']
            details = form.cleaned_data['asset_details']
            address = form.cleaned_data['asset_address']
            contact = form.cleaned_data['asset_contact']
            temp = Assets(name=name, details=details, address=address, contact=contact, 
                owner=request.user)
            temp.save()

    assets = Assets.objects.filter(owner=request.user)

    return render(request=request, template_name="abcd/step3.html", context={"assets": assets})


@login_required(login_url='/login')
def step4(request: HttpRequest):
    form = addInstitutionForm(request.POST or None)
    if request.method == "POST":
        print(request.user)
        if not form.is_valid():
            print("invalid")
        else:
            name = form.cleaned_data['institution_name']
            details = form.cleaned_data['institution_details']
            address = form.cleaned_data['institution_address']
            contact = form.cleaned_data['institution_contact']
            temp = Institutions(name=name, details=details, address=address, contact=contact, 
                owner=request.user)
            temp.save()

    institutions = Institutions.objects.filter(owner=request.user)
    return render(request=request, template_name="abcd/step4.html", context={"institutions": institutions})

@login_required(login_url='/login')
def step5(request: HttpRequest):
    if request.method == "POST":
        # [{"from": "Alpha", "to": "Beta"}, {"from": "Gamma", "to": "Delta"}]
        # from institutions to stakeholders
        print(request.body)
        print(json.loads(request.body).keys())
        dataDict = json.loads(request.body)

        profile = Profile.objects.get(id=request.user.id)
        assocsString = profile.assocs
        if assocsString == "":
            assocsString = "[]"
            
        for x in dataDict.keys():
            for y in dataDict[x]:
                assocsString = appendToStringList(
                    assocsString, 
                    createConnString(x, y["name"])
                    )
        profile.assocs = assocsString
        profile.save()

    profile = Profile.objects.get(id=request.user.id)
    assocsString = profile.assocs or "[]"
    institutions = Institutions.objects.filter(owner=request.user)
    listInsts = []
    for inst in institutions.iterator():
        listInsts.append(json.dumps({
            "name": inst.name,
            "details": inst.details,
            "address": inst.address,
            "contact": inst.contact,
            "stakeholders": filterFromConnString(assocsString, inst.name)
        }))

    stakeholders = Stakeholders.objects.filter(owner=request.user)
    listStakes = []
    
    for stake in stakeholders.iterator():
        listStakes.append(json.dumps({
            "name": stake.name
        }))

    dataDict = {"institutions": listInsts, "stakeholders": listStakes}
    data = json.dumps(dataDict)
    return render(request=request, template_name="abcd/step5.html", context={"data": data})

@login_required(login_url='/login')
def results(request: HttpRequest):
    a = generateSuggestions(request.user)
    a_format = list(map(mapper, a))
    json = generateJson(request.user)
    print(a_format)
    return render(request=request, template_name="abcd/finalGraph.html", context={"data": json, "suggestions": a_format})

def mapper(sett):
    return "Association missing between " + list(sett)[0] + " and " + list(sett)[1]
def home(request: HttpRequest):
    return render(request=request, template_name="abcd/home.html")


def save_graph(request: HttpRequest):
    data = json.loads(request.POST.get('data', ''))
    d = json.loads(data)
    nodes = d['nodeDataArray']
    nodes_name = list(map(lambda obj: obj['key'], nodes))
    db_nodes = Node.objects.filter(owner=request.user)
    for db_node in db_nodes:
        if db_node.name not in nodes_name:
            db_node.delete()

    for node in nodes:
        color = node['color']
        x_y = node['loc'].split()
        if color == "yellow": # tags
            target = Tags.objects.filter(owner=request.user).get(name=node['key'])
        elif color == "lightblue":  # stakeholder
            target = Stakeholders.objects.filter(owner=request.user).get(name=node['key'])
        elif color == "red": # assets
            target = Assets.objects.filter(owner=request.user).get(name=node['key'])
        elif color == "blue": # institution
            target = Institutions.objects.filter(owner=request.user).get(name=node['key'])
        target.x_coord = x_y[0]
        target.y_coord = x_y[1]
        target.save()
    assocs = d['linkDataArray']
    profile = Profile.objects.get(id=request.user.id)
    profile.assocs = json.dumps(assocs)
    profile.save()


    return HttpResponse(json.dumps({}),
                    content_type="application/json")

def assoc_set(assocs):
    for assoc in assocs:
        assoc

def generateSuggestions(user):
    a = genSets(user.assocs)
    stakeholders = list(Stakeholders.objects.filter(owner=user))
    stake_permu = []
    for stakeholder in stakeholders:
        for stakeholder2 in stakeholders:
            if not stakeholder == stakeholder2 :
                temp = set()
                temp.add(stakeholder.name)
                temp.add(stakeholder2.name)
                if temp not in stake_permu and temp not in a:
                    stake_permu.append(temp)
    print(stake_permu)
    return stake_permu

def genSets(assocs):
    if assocs == "":
        return []
    d = json.loads(assocs)
    output = []
    for a in d:
        temp = set()
        temp.add(a["from"])
        temp.add(a["to"])
        if temp not in output:
            output.append(temp)
    return output

#supporting function
def generateJson(user):
    nodes = []
    nodes.extend(Tags.objects.filter(owner=user))
    nodes.extend(Stakeholders.objects.filter(owner=user))
    nodes.extend(Assets.objects.filter(owner=user))
    nodes.extend(Institutions.objects.filter(owner=user))
    nodes_dic = []
    nodes_dic.extend(map(lambda obj: obj.get_dict(), nodes))
    assocs = []
    if (not user.assocs == ""):
        data = json.loads(user.assocs)
        assocs = data
    d = dict()
    d["class"] = "GraphLinksModel"
    d["linkLabelKeysProperty"] =  "labelKeys"
    d["nodeDataArray"] = nodes_dic
    d["linkDataArray"] = assocs
    json_object = json.dumps(d, indent=4)
    return json_object

def createConnString(fromItem, toItem):
    connString = "{"
    connString += "\"from\":" + "\"" + fromItem + "\""
    connString += ","
    connString += "\"to\":" + "\"" + toItem + "\""
    connString += "}"
    return connString

def appendToStringList(stringList, item):
    if stringList == "[]":
        return "[" + item + "]"

    if stringList.find(item) >= 0:
        return stringList
    return stringList[:-1] + "," + item + "]"


def filterFromConnString(assocs : str, item : str) -> list:
    # Gets a set of connections from/to the item
    d = json.loads(assocs)
    temp = set()

    for a in d:
        if a["from"] == item:
            temp.add(a["to"])
        if a["to"] == item:
            temp.add(a["from"])
    return list(temp)
