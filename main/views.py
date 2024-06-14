from django.shortcuts import render, HttpResponse
from .aa import data
import json
from django.core.serializers import serialize
from django.db.models import Max
from .qq import IITS, BRANCHES, SEAT_TYPES, GENDERS, YEARS
# Create your views here.
from django.db.models import Avg
from django.core.paginator import Paginator


def dashboard(request):
    return render(request, 'main/dashboard.html')


def base(request):
    context = {
        'colleges': IITS,
        'branches': BRANCHES,
        'seat_types': SEAT_TYPES,
        'genders': GENDERS,
    }
    return render(request, 'main/base.html', context)


def upload_csv(request):
    if request.method == 'POST':
        print(request.FILES)
        csv_file = request.FILES['document']
        file_data = csv_file.read().decode('utf-8')
        csv_data = file_data.split('\n')
        for x in csv_data:
            fields = x.split(',')
            print(fields)
            info = data(institute=fields[1], program=fields[2], seat_type=fields[3], gender=fields[4], opening_rank=fields[5],
                        closing_rank=fields[6], year=fields[7], roundNo=fields[8], institute_type=fields[10])
            info.save()
    return render(request, 'main/upload.html')


def filter(request):
  alldata = data.objects.all()[:50]
  if request.method == 'POST' and 'apply_filter' in request.POST:
        filters={}
        year = request.POST.get('year',None)
        gender = request.POST.getlist('gender',None)
        college = request.POST.getlist('college',None)
        branch = request.POST.getlist('branch',None)
        seat_type = request.POST.getlist('seat_type',None)
        if year:
            filters['year__in']=year
        if gender:
            filters['gender__in']=gender
        if college:
            filters['institute__in']=college
        if branch:
            filters['program__in']=branch
        if seat_type:
            filters['seat_type__in']=seat_type
        alldata = data.objects.filter(**filters)[:50]
        context = {
            'alldata': alldata,
            'colleges': IITS,
            'branches': BRANCHES,
            'seat_types': SEAT_TYPES,
            'genders': GENDERS,
            'years': YEARS,
            'isCollegeNeeded': "True",
            'isBranchNeeded': "True",
            'isSeatTypeNeeded': "True",
            'isGenderNeeded': "True",
            'isYearNeeded': "True",
        }
        return render(request, 'main/filter.html',context)
  else:
    context = {
        'alldata': alldata,
        'colleges': IITS,
        'branches': BRANCHES,
        'years': YEARS,
        'seat_types': SEAT_TYPES,
        'genders': GENDERS,
        'isCollegeNeeded': "True",
        'isBranchNeeded': "True",
        'isSeatTypeNeeded': "True",
        'isGenderNeeded': "True",
        'isYearNeeded': "True",
    }
    return render(request, 'main/filter.html', context)


def printdata(request):

    context = {
        'colleges': IITS,
        'branches': BRANCHES,
        'seat_types': SEAT_TYPES,
        'genders': GENDERS,
        'isCollegeNeeded': "True",
        'isBranchNeeded': "True",
        'isSeatTypeNeeded': "True",
        'isGenderNeeded': "True",
        'isYearNeeded': "False",
    }
    if request.method == 'POST':
        seat_type = request.POST.get('seat_type')
        institute = request.POST.get('college')
        branch_name = request.POST.get('branch')
        gender = request.POST.get('gender')
        alldata = data.objects.filter(
            seat_type=seat_type, institute=institute, gender=gender, program=branch_name).all()

        jsdata = alldata.values('year', 'closing_rank', 'roundNo', 'program')
        jsdata = list(jsdata)
        jsdata = json.dumps(jsdata)
        context1 = {
            'colleges': IITS,
            'branches': BRANCHES,
            'seat_types': SEAT_TYPES,
            'genders': GENDERS,
            'alldata': alldata,
            'jsdata': jsdata,
            'isCollegeNeeded': "True",
            'isBranchNeeded': "True",
            'isSeatTypeNeeded': "True",
            'isGenderNeeded': "True",
            'isYearNeeded': "False",
        }
        return render(request, 'main/index.html', context1)

    return render(request, 'main/index.html', context)


def trenddual(request):
    if request.method == 'POST':
        filters = {'roundNo': 6, 'program__contains': 5}
        filter_gender = request.POST.getlist('gender', None)
        filter_institute = request.POST.getlist('college', None)
        filter_seat = request.POST.getlist('seat_type', None)
        # print(filter_institute)
        if filter_gender:
            filters['gender__in'] = filter_gender
        if filter_institute:
            filters['institute__in'] = filter_institute
        if filter_seat:
            filters['seat_type__in'] = filter_seat
        # print(filters)
        # dualdata = data.objects.filter(program__contains='5', roundNo=6)

        dualdata = data.objects.filter(**filters)
    else:
        dualdata = data.objects.filter(program__contains='5', roundNo=6)

    year_set = set()
    branches = {'computer': "Computer Science", 'electrical': 'Electrical/Electronics Engineering',
                'electronics': 'Electrical/Electronics Engineering', 'math': 'Mathematics', 'physics': 'Physics', 'chemical': 'Chemical Engineering', 'mech': 'Mechanical Engineering'}
    options = ['computer', 'electrical', 'electronics',
               'math', 'physics', 'chemical', 'mech']
    dataset = {}
    for val in dualdata:
        dict = {}
        flag = ''
        for branch in options:
            if branch in val.program.lower():
                flag = branches[branch]
                break
        if flag:
            year_set.add(val.year)
            if flag in dataset:
                if val.year in dataset[flag]:
                    dataset[flag][val.year].append(
                        int(val.opening_rank+val.closing_rank)/2)
                else:
                    dataset[flag][val.year] = []
                    dataset[flag][val.year].append(
                        int(val.opening_rank+val.closing_rank)/2)
            else:
                dataset[flag] = {}
                dataset[flag][val.year] = []
                dataset[flag][val.year].append(
                    int(val.opening_rank+val.closing_rank)/2)

    # print(dataset)
    colors = [
        "#ae1029",
        "#0065c2",
        "#26c238",
        "#9876aa",
        "#fb8649",
        "#57904b",
        "#d35b5c",
    ]
    i = 0
    final = []
    branches = []
    for k, v in dataset.items():
        branches.append(k)

        dict = {}
        dict['name'] = k
        dict['type'] = 'line'
        dict['smooth'] = True
        dict['color'] = colors[i]
        dict['data'] = []
        # print(v, '\n')
        for year in year_set:
            # print(year)
            if year in v:
                dict['data'].append(int((sum(v[year]))/len(v[year])))
            else:
                dict['data'].append(None)
        final.append(dict)
        i += 1

    context = {
        'alldata': dualdata,
        'data': json.dumps(final), 'year': json.dumps(list(year_set)), 'branches': branches, 'seat_types': SEAT_TYPES, 'colleges': IITS, 'genders': GENDERS, 'isCollegeNeeded': "False",
        'question': 'How has the trend of students opting for dual degree programs (B.Tech + M.Tech) changed over the years? ',
        'isBranchNeeded': "False",
        'isSeatTypeNeeded': "True",
        'isGenderNeeded': "True",
        'isYearNeeded': "False",
        'isCollegeNeeded': 'True'
    }
    # if request.method == 'POST':
    return render(request, 'main/akshat_q1.html', context)


def trendspecial(request):
    if request.method == 'POST':
        filters = {'roundNo': 6}
        filter_gender = request.POST.get('gender', None)
        filter_institute = request.POST.get('college_name', None)
        filter_seat = request.POST.get('seat_type', None)
        if filter_gender is not None:
            filters['gender'] = filter_gender
        if filter_institute is not None:
            filters['institute'] = filter_institute
        if filter_seat is not None:
            filters['seat_type'] = filter_seat
        dualdata = data.objects.filter(**filters)
    else:
        dualdata = data.objects.filter(roundNo=6)
    year_set = set()

    branches = {'computer': "Computer Science",
                'aero': 'Aerospace', 'bio': 'Bio Technology', 'arti': 'Data Science Artificial Intelligence', 'data': 'Data Science Artificial Intelligence', 'textile': 'Textile', 'agri': 'Agricultural', 'instru': 'Instrumental', 'ocean': 'Ocean and Naval'}
    options = ['computer', 'aero', 'bio', 'arti', 'textile', 'agri', 'instru', 'ocean', 'data'
               ]
    dataset = {}
    for val in dualdata:
        dict = {}
        flag = ''
        for branch in options:
            if branch in val.program.lower():
                flag = branches[branch]
                break
        if flag:
            year_set.add(val.year)
            if flag in dataset:
                if val.year in dataset[flag]:
                    dataset[flag][val.year].append(
                        int(val.opening_rank+val.closing_rank)/2)
                else:
                    dataset[flag][val.year] = []
                    dataset[flag][val.year].append(
                        int(val.opening_rank+val.closing_rank)/2)
            else:
                dataset[flag] = {}
                dataset[flag][val.year] = []
                dataset[flag][val.year].append(
                    int(val.opening_rank+val.closing_rank)/2)

    # print(dataset)
    colors = [
        "#ae1029",
        "#0065c2",
        "#26c238",
        "#9876aa",
        "#fb8649",
        "#57904b",
        "#d35b5c",
    ]
    i = 0
    final = []
    branches = []
    for k, v in dataset.items():
        dict = {}
        dict['name'] = k
        dict['type'] = 'line'
        dict['smooth'] = True
        dict['color'] = colors[i]
        dict['data'] = []
        for year in year_set:
            if year in v:
                dict['data'].append(int((sum(v[year]))/len(v[year])))
            else:
                dict['data'].append(None)
        final.append(dict)
        i += 1
    context = {
        'data': json.dumps(final),
        'alldata':dualdata,
        'year': json.dumps(list(year_set)),
        'seat_type': SEAT_TYPES,
        'colleges': IITS,
        'gender': GENDERS,
        'question': "How has the preference for specialized branches (such as Aerospace, Biotechnology, Computer Science, etc.) evolved over time?",
        'isBranchNeeded': "False",
        'isSeatTypeNeeded': "True",
        'isGenderNeeded': "True",
        'isYearNeeded': "False",
        'isCollegeNeeded': 'True',

    }
    # if request.method == 'POST':
    return render(request, 'main/akshat_q1.html', context)


def dig_q1(request):
    popular_branches = [
        'Computer Science and Engineering (4 Years Bachelor of Technology)',
        'Electrical Engineering (4 Years Bachelor of Technology)',
        'Mechanical Engineering (4 Years Bachelor of Technology)',
        'Mathematics and Computing (4 Years Bachelor of Technology)',
    ]

    if request.method == 'POST' and 'apply_filter' in request.POST:
        gender = request.POST.getlist('gender')
        college = request.POST.getlist('college')
        # branch = request.POST.getlist('branch')
        seat_type = request.POST.getlist('seat_type')
        filtered_data = data.objects.filter(
            roundNo='6', seat_type__in=seat_type, gender__in=gender, program__in=popular_branches, institute__in=college)
        filtered_data = filtered_data.order_by(
            '-year', 'institute', 'program', 'opening_rank', )
        jsdata = filtered_data.values(
            'institute', 'year', 'program', 'opening_rank', 'closing_rank')
        jsdata = list(jsdata.order_by(
            'institute', 'opening_rank', 'program', '-year', ))
        jsdata = json.dumps(jsdata)

        context = {
            'alldata': filtered_data,
            'jsdata': jsdata,
            'isCollegeNeeded': "True",
            'isBranchNeeded': "True",
            'isSeatTypeNeeded': "True",
            'isGenderNeeded': "True",
            'isYearNeeded': "False",
            'years': YEARS,
            'colleges': IITS,
            'branches': BRANCHES,
            'seat_types': SEAT_TYPES,
            'genders': GENDERS,
        }

        return render(request, 'main/digvijay_q1.html', context)
    
    else:
        filtered_data = data.objects.filter(roundNo='6', seat_type='OPEN', gender='Gender-Neutral', program__in=popular_branches)
        filtered_data= filtered_data.order_by('-year', 'institute', 'program','opening_rank', )
        jsdata = filtered_data.values('institute', 'year', 'program', 'opening_rank', 'closing_rank')
        jsdata = list(jsdata.order_by('institute', 'opening_rank', 'program','-year', ))
        jsdata = json.dumps(jsdata)

        context = {
            'alldata': filtered_data,
            'jsdata': jsdata,
            'isCollegeNeeded':"True",
            'isBranchNeeded':"True",
            'isSeatTypeNeeded':"True",
            'isGenderNeeded':"True",
            'isYearNeeded':"False",
            'years':YEARS,
            'colleges':IITS,
            'branches':BRANCHES,
            'seat_types':SEAT_TYPES,
            'genders':GENDERS,
        }

        return render(request, 'main/digvijay_q1.html', context)


def sid_q1(request):
    if request.method == 'POST' and 'apply_filter' in request.POST:
        filters = {'roundNo': 6}
        gender = request.POST.getlist('gender', None)
        college = request.POST.getlist('college', None)
        seat_type = request.POST.getlist('seat_type', None)
        if gender:
            filters['gender__in'] = gender
        if college:
            filters['institute__in'] = college
        if seat_type:
            filters['seat_type__in'] = seat_type

        filtered_data = data.objects.filter(**filters)
        filtered_data = filtered_data.order_by('-year', 'institute', 'program', 'opening_rank')
        jsdata = filtered_data.values('institute', 'year', 'program', 'opening_rank', 'closing_rank')
        jsdata = list(jsdata.order_by('institute', 'opening_rank', 'program', '-year'))
        jsdata = json.dumps(jsdata)

        context = {
            'alldata': filtered_data,
            'jsdata': jsdata,
            'isCollegeNeeded': "True",
            'isBranchNeeded': "False",
            'isSeatTypeNeeded': "True",
            'isGenderNeeded': "True",
            'isYearNeeded': "False",
            'years': YEARS,
            'colleges': IITS,
            'branches': BRANCHES,
            'seat_types': SEAT_TYPES,
            'genders': GENDERS,
        }

        return render(request, 'main/siddhant_q1.html', context)

    else:  
        all_data = data.objects.filter(
            roundNo='6', seat_type='OPEN', gender='Gender-Neutral')
        jsdata = all_data.values(
            'institute', 'year', 'program', 'opening_rank', 'closing_rank')
        jsdata = json.dumps(list(jsdata))
        context = {
            'alldata': all_data,
            'jsdata': jsdata,
            'isCollegeNeeded':"True",
            'isBranchNeeded':"False",
            'isSeatTypeNeeded':"True",
            'isGenderNeeded':"True",
            'isYearNeeded':"False",
            'years':YEARS,
            'colleges':IITS,
            'branches':BRANCHES,
            'seat_types':SEAT_TYPES,
            'genders':GENDERS,
        }
        return render(request, 'main/siddhant_q1.html', context)


def sid_q2(request):
 if request.method == 'POST' and 'apply_filter' in request.POST:
        filters = {'roundNo': 6}
        gender = request.POST.getlist('gender', None)
        college = request.POST.getlist('college', None)
        seat_type = request.POST.getlist('seat_type', None)
        if gender:
            filters['gender__in'] = gender
        if college:
            filters['institute__in'] = college
        if seat_type:
            filters['seat_type__in'] = seat_type

        filtered_data = data.objects.filter(**filters)
        filtered_data = filtered_data.order_by('-year', 'institute', 'program', 'opening_rank')
        jsdata = filtered_data.values('institute', 'year', 'program', 'opening_rank', 'closing_rank')
        jsdata = list(jsdata.order_by('institute', 'opening_rank', 'program', '-year'))
        jsdata = json.dumps(jsdata)

        context = {
            'alldata': filtered_data,
            'jsdata': jsdata,
            'isCollegeNeeded': "True",
            'isBranchNeeded': "False",
            'isSeatTypeNeeded': "True",
            'isGenderNeeded': "True",
            'isYearNeeded': "False",
            'years': YEARS,
            'colleges': IITS,
            'branches': BRANCHES,
            'seat_types': SEAT_TYPES,
            'genders': GENDERS,
        }

        return render(request, 'main/siddhant_q2.html', context)

 else:   
    colleges = [i[0] for i in IITS]
    all_data = data.objects.filter(
        roundNo='6', seat_type='OPEN', gender='Gender-Neutral', institute__in=colleges)
    jsdata = all_data.values(
        'institute', 'year', 'program', 'opening_rank', 'closing_rank')
    jsdata = json.dumps(list(jsdata))
    context = {
        'alldata': all_data,
        'jsdata': jsdata,
        'isCollegeNeeded':"True",
        'isBranchNeeded':"False",
        'isSeatTypeNeeded':"True",
        'isGenderNeeded':"True",
        'isYearNeeded':"False",
        'years':YEARS,
        'colleges':IITS,
        'branches':BRANCHES,
        'seat_types':SEAT_TYPES,
        'genders':GENDERS,
    }
    return render(request, 'main/siddhant_q2.html', context)


def sid_q3(request):
 if request.method == 'POST' and 'apply_filter' in request.POST:
        filters = {'roundNo': 6}
        gender = request.POST.getlist('gender', None)
        college = request.POST.getlist('college', None)
        seat_type = request.POST.getlist('seat_type', None)
        if gender:
            filters['gender__in'] = gender
        if college:
            filters['institute__in'] = college
        if seat_type:
            filters['seat_type__in'] = seat_type

        filtered_data = data.objects.filter(**filters)
        filtered_data = filtered_data.order_by('-year', 'institute', 'program', 'opening_rank')
        jsdata = filtered_data.values('institute', 'year', 'program', 'opening_rank', 'closing_rank')
        jsdata = list(jsdata.order_by('institute', 'opening_rank', 'program', '-year'))
        jsdata = json.dumps(jsdata)

        context = {
            'alldata': filtered_data,
            'jsdata': jsdata,
            'isCollegeNeeded': "True",
            'isBranchNeeded': "False",
            'isSeatTypeNeeded': "True",
            'isGenderNeeded': "True",
            'isYearNeeded': "False",
            'years': YEARS,
            'colleges': IITS,
            'branches': BRANCHES,
            'seat_types': SEAT_TYPES,
            'genders': GENDERS,
        }

        return render(request, 'main/siddhant_q3.html', context)
 else:   
    colleges = [i[0] for i in IITS]
    all_data = data.objects.filter(
        roundNo='6', seat_type='OPEN', gender='Gender-Neutral', institute__in=colleges)
    jsdata = all_data.values(
        'institute', 'year', 'program', 'opening_rank', 'closing_rank')
    jsdata = json.dumps(list(jsdata))
    context = {
        'alldata': all_data,
        'jsdata': jsdata,
        'isCollegeNeeded':"True",
        'isBranchNeeded':"False",
        'isSeatTypeNeeded':"True",
        'isGenderNeeded':"True",
        'isYearNeeded':"False",
        'years':YEARS,
        'colleges':IITS,
        'branches':BRANCHES,
        'seat_types':SEAT_TYPES,
        'genders':GENDERS,
    }
    return render(request, 'main/siddhant_q3.html', context)


def dev_q3(request):
    filtered_data = data.objects.filter(roundNo='6')

    seat_types = ['OPEN', 'EWS', 'SC', 'ST', 'OBC-NCL']
    result = []

    for seat_type in seat_types:
        for year in range(2000, 2024):  # Assuming the range of years you want to consider
            max_closing_rank = filtered_data.filter(
                seat_type=seat_type, year=year).aggregate(Max('closing_rank'))
            if max_closing_rank['closing_rank__max']:
                obj = filtered_data.filter(
                    seat_type=seat_type, year=year, closing_rank=max_closing_rank['closing_rank__max']).first()
                result.append({
                    'seat_type': obj.seat_type,
                    'year': obj.year,
                    'closing_rank': obj.closing_rank,
                    'institute': obj.institute,
                    'institute_type':"IIT",
                    # 'institute_type':obj.institute_type,         ##giving error for some reason
                    'program':obj.program,
                    'gender':obj.gender,
                    'opening_rank':obj.opening_rank,
                    'roundNo':obj.roundNo,
                    # Add more fields if necessary
                })

    jsdata = json.dumps(result)
    context = {
        'alldata': result,
        'jsdata': jsdata,
    }
    return render(request, 'main/dev_q3.html', context)


def dig_q2(request):
 if request.method == 'POST' and 'apply_filter' in request.POST:
        year = request.POST.get('year')
        gender = request.POST.get('gender')
        college = request.POST.getlist('college')
        branch = request.POST.getlist('branch')
        seat_type = request.POST.getlist('seat_types')
        if (year == None):
            year = 2016

        print(year)

        # for option in college:
        #     print(option)
        # print(college)
        filtered_data = data.objects.filter(year=(year), roundNo='6', seat_type='OPEN', gender='Gender-Neutral', closing_rank__lt='1000', program__contains='4').filter(
            program__contains='Technology').exclude(program__contains='Mechanical').exclude(program__contains='Power').exclude(program__contains='Physics')
        jsdata = filtered_data.values(
            'institute', 'year', 'program', 'opening_rank', 'closing_rank')
        jsdata = json.dumps(list(jsdata))
        context = {
            'alldata': filtered_data,
            'jsdata': jsdata,
            'years': YEARS,
            'year': year,
            'colleges': IITS,
            'branches': BRANCHES,
            'seat_types': SEAT_TYPES,
            'genders': GENDERS,
            'isCollegeNeeded': "False",
            'isBranchNeeded': "False",
            'isSeatTypeNeeded': "False",
            'isGenderNeeded': "False",
            'isYearNeeded': "True",

        }
        return render(request, 'main/digvijay_q2.html', context)
 else:
    year = 2016
    filtered_data = data.objects.filter(year=year, roundNo='6', seat_type='OPEN', gender='Gender-Neutral', closing_rank__lt='1000', program__contains='4').filter(
        program__contains='Technology').exclude(program__contains='Mechanical').exclude(program__contains='Power').exclude(program__contains='Physics')

    jsdata = filtered_data.values(
        'institute', 'year', 'program', 'opening_rank', 'closing_rank')
    jsdata = json.dumps(list(jsdata))
    context = {
        'alldata': filtered_data,
        'jsdata': jsdata,
        'years': YEARS,
        'year': year,
        'colleges': IITS,
        'branches': BRANCHES,
        'seat_types': SEAT_TYPES,
        'genders': GENDERS,
        'isCollegeNeeded': "False",
        'isBranchNeeded': "False",
        'isSeatTypeNeeded': "False",
        'isGenderNeeded': "False",
        'isYearNeeded': "True",
    }

    return render(request, 'main/digvijay_q2.html', context)


def Moh_q1(request):
    new_iits = [
        # Add more New IITs as needed
        'Indian Institute of Technology Gandhinagar',
        'Indian Institute of Technology Jodhpur',
        'Indian Institute of Technology Patna',
        'Indian Institute of Technology Mandi',
        'Indian Institute of Technology Palakkad',
        'Indian Institute of Technology Ropar',
        'Indian Institute of Technology Jammu',
        'Indian Institute of Technology Goa',
        'Indian Institute of Technology Bhilai',
        'Indian Institute of Technology (ISM) Dhanbad',
        'Indian Institute of Technology Tirupati',
    ]

    old_iits = [
        'Indian Institute of Technology Bombay',
        # Add more Old IITs as needed
        'Indian Institute of Technology Delhi',
        'Indian Institute of Technology Kanpur',
        'Indian Institute of Technology Madras',
        'Indian Institute of Technology Kharagpur',
        'Indian Institute of Technology Roorkee',
        'Indian Institute of Technology Guwahati',
    ]

    # Retrieve the unique years from the data
    years = data.objects.values_list('year', flat=True).distinct()

    # Calculate the average closing rank for each year for New IITs
    new_iit_avg_ranks = []
    for year in years:
        new_iit_data = data.objects.filter(
            roundNo='6',
            seat_type='OPEN',
            gender='Gender-Neutral',
            institute__in=new_iits,
            program='Computer Science and Engineering (4 Years Bachelor of Technology)',
            year=year
        ).aggregate(avg_closing_rank=Avg('closing_rank'))
        new_iit_avg_ranks.append({
            'year': year,
            'avg_closing_rank': new_iit_data['avg_closing_rank']
        })

    # Calculate the average closing rank for each year for Old IITs
    old_iit_avg_ranks = []
    for year in years:
        old_iit_data = data.objects.filter(
            roundNo='6',
            seat_type='OPEN',
            gender='Gender-Neutral',
            institute__in=old_iits,
            program='Computer Science and Engineering (4 Years Bachelor of Technology)',
            year=year
        ).aggregate(avg_closing_rank=Avg('closing_rank'))
        old_iit_avg_ranks.append({
            'year': year,
            'avg_closing_rank': old_iit_data['avg_closing_rank']
        })

    # Convert the data to JSON format
    new_iit_json_data = json.dumps(new_iit_avg_ranks)
    old_iit_json_data = json.dumps(old_iit_avg_ranks)
    # print(years)
    # print(new_iit_json_data)
    # print(old_iit_json_data)
    context = {
        'question': 'What is the Popularity Variation between New and Old IITs? ',
        'years': years,
        'new_iit_data': new_iit_json_data,
        'old_iit_data': old_iit_json_data,
    }

    return render(request, 'main/Mohit_q1.html', context)


def Moh_q1exp(request):
    new_iits = [
        'Indian Institute of Technology Dharwad',
        # Add more New IITs as needed
        'Indian Institute of Technology Gandhinagar',
        'Indian Institute of Technology Jodhpur',
        'Indian Institute of Technology Patna',
        'Indian Institute of Technology Mandi',
        'Indian Institute of Technology Palakkad',
        'Indian Institute of Technology Ropar',
        'Indian Institute of Technology Jammu',
        'Indian Institute of Technology Goa',
        'Indian Institute of Technology Bhilai',
        'Indian Institute of Technology (ISM) Dhanbad',
        'Indian Institute of Technology Tirupati',
    ]

    # Initialize an empty list to store the institute data
    institute_data = []

    # Retrieve the unique years in the data
    years = data.objects.filter(
        roundNo='6',
        seat_type='OPEN',
        gender='Gender-Neutral',
        institute__in=new_iits,
        program='Computer Science and Engineering (4 Years Bachelor of Technology)'
    ).values_list('year', flat=True).distinct().order_by('year')

    # Iterate over each institute
    for institute in new_iits:
        # Filter data for the current institute
        institute_data_queryset = data.objects.filter(
            roundNo='6',
            seat_type='OPEN',
            gender='Gender-Neutral',
            institute=institute,
            program='Computer Science and Engineering (4 Years Bachelor of Technology)'
        ).values('year').annotate(avg_closing_rank=Avg('closing_rank')).order_by('year')

        # Convert the queryset to a list of dictionaries
        institute_data_list = list(institute_data_queryset)

        # Add the institute name and data to the institute_data list
        institute_data.append({
            'name': institute,
            'data': institute_data_list
        })

    # Convert the institute_data to JSON format
    institute_data_json = json.dumps(institute_data)

    context = {
        'institute_data': institute_data_json,
    }

    return render(request, 'main/Mohit_q1exp.html', context)


def Moh_q1exp2(request):
    old_iits = [
        'Indian Institute of Technology Bombay',
        # Add more Old IITs as needed
        'Indian Institute of Technology Delhi',
        'Indian Institute of Technology Kanpur',
        'Indian Institute of Technology Madras',
        'Indian Institute of Technology Kharagpur',
        'Indian Institute of Technology Roorkee',
        'Indian Institute of Technology Guwahati',
    ]

    # Initialize an empty list to store the institute data
    institute_data = []

    # Retrieve the unique years in the data
    years = data.objects.filter(
        roundNo='6',
        seat_type='OPEN',
        gender='Gender-Neutral',
        institute__in=old_iits,
        program='Computer Science and Engineering (4 Years Bachelor of Technology)'
    ).values_list('year', flat=True).distinct().order_by('year')

    # Iterate over each institute
    for institute in old_iits:
        # Filter data for the current institute
        institute_data_queryset = data.objects.filter(
            roundNo='6',
            seat_type='OPEN',
            gender='Gender-Neutral',
            institute=institute,
            program='Computer Science and Engineering (4 Years Bachelor of Technology)'
        ).values('year').annotate(avg_closing_rank=Avg('closing_rank')).order_by('year')

        # Convert the queryset to a list of dictionaries
        institute_data_list = list(institute_data_queryset)

        # Add the institute name and data to the institute_data list
        institute_data.append({
            'name': institute,
            'data': institute_data_list
        })

    # Convert the institute_data to JSON format
    institute_data_json = json.dumps(institute_data)

    context = {
        'institute_data': institute_data_json,
    }

    return render(request, 'main/Mohit_q1exp2.html', context)


def branch_popularity(request):
    # Retrieve the unique years in the data
    years = data.objects.values_list(
        'year', flat=True).distinct().order_by('year')

    # Retrieve all branch data
    all_branches = data.objects.values('program').distinct()

    # Initialize the paginator with the all_branches queryset and number of branches per page
    paginator = Paginator(all_branches, 10)

    # Get the current page number from the request query parameters
    page_number = request.GET.get('page')

    # Get the branches for the current page
    branches = paginator.get_page(page_number)

    # Initialize an empty list to store the branch data
    branch_data = []

    # Iterate over each branch
    for branch in branches:
        # Filter data for the current branch
        branch_data_queryset = data.objects.filter(program=branch['program']).values(
            'year').annotate(avg_closing_rank=Avg('closing_rank')).order_by('year')

        # Convert the queryset to a list of dictionaries
        branch_data_list = list(branch_data_queryset)

        # Add the branch name and data to the branch_data list
        branch_data.append({
            'name': branch['program'],
            'data': branch_data_list
        })

    # Convert the branch_data to JSON format
    branch_data_json = json.dumps(branch_data)

    context = {
        'branch_data': branch_data_json,
        'years': json.dumps(list(years)),  # Convert years to JSON format
        'branches': branches,  # Pass the paginated branches to the template
    }

    return render(request, 'main/branch_popularity.html', context)
