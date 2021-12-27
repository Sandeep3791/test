from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from wayrem_admin.models import Ingredients
from django.contrib.auth.decorators import login_required
from wayrem_admin.forms import IngredientsCreateForm
import pandas as pd
from sqlalchemy import create_engine
import uuid
from wayrem.settings import DATABASES
from pymysql import connect
from django.core.paginator import Paginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from wayrem_admin.export import generate_excel


def ingredient_excel(request):
    return generate_excel("ingredient_master", "ingredients")


@login_required(login_url='wayrem_admin:root')
def create_ingredients(request):
    context = {}
    # user = SupplierProfileModel.objects.filter(user_id = request.user.id).first()
    form = IngredientsCreateForm(request.POST or None)
    context['form'] = form
    if request.method == "POST":
        print("POST")
        if form.is_valid():
            print('valid')
            form.save()
            return redirect('wayrem_admin:ingredientslist')
        else:
            print("Invalid")
    return render(request, 'create_ingredients.html', context)


# class IngredientsList(View):
#     template_name = "ingredientslist.html"

#     @method_decorator(login_required(login_url='/'))
#     def get(self, request, format=None):
#         ingredientslist = Ingredients.objects.all()
#         # user_role = Roles.objects.all()
#         # "roles":user_role
#         return render(request, self.template_name, {"ingredientslist": ingredientslist})


def ingredientsList(request):
    ingredients_list = Ingredients.objects.all()
    paginator = Paginator(ingredients_list, 5)
    page = request.GET.get('page')
    try:
        ingredientslist = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        ingredientslist = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        ingredientslist = paginator.page(paginator.num_pages)
    return render(request, "ingredientslist.html", {"list": ingredientslist})


class DeleteIngredients(View):
    def post(self, request):
        ingredientsid = request.POST.get('ingredients_id')
        ingredients = Ingredients.objects.get(id=ingredientsid)
        ingredients.delete()
        return redirect('wayrem_admin:ingredientslist')


@login_required(login_url='wayrem_admin:root')
def update_ingredients(request, id=None, *args, **kwargs):
    print(id)
    if request.method == "POST":
        # kwargs = { 'data' : request.POST }
        user = Ingredients.objects.get(id=id)
        form = IngredientsCreateForm(
            request.POST or None, instance=user)
        if form.is_valid():
            print("FORM")
            ingredients_name = form.cleaned_data['ingredients_name']
            ingredients_status = form.cleaned_data['ingredients_status']
            user.ingredients_name = ingredients_name
            user.ingredients_status = ingredients_status
            user.save()
            print("Here")
            return redirect('wayrem_admin:ingredientslist')
    else:
        user = Ingredients.objects.get(id=id)
        form = IngredientsCreateForm(instance=user)
    return render(request, 'update_ingredients.html', {'form': form, 'id': user.id})


def import_ingredients(request):
    if request.method == "POST":
        try:
            file = request.FILES["myFileInput"]
            engine = create_engine(
                f"mysql+pymysql://{DATABASES['default']['USER']}:{DATABASES['default']['PASSWORD']}@{DATABASES['default']['HOST']}/{DATABASES['default']['NAME']}?charset=utf8")
            # engine = create_engine(
            #     "mysql+pymysql://admin:Merlin007#@wayrem.c08qmktlafbu.us-east-1.rds.amazonaws.com/wayrem_8.2?charset=utf8")
            # df = pd.read_excel('files/ingredients.xlsx')
            con = connect(user=DATABASES['default']['USER'], password=DATABASES['default']['PASSWORD'],
                          host=DATABASES['default']['HOST'], database=DATABASES['default']['NAME'])
            # con = connect(user="admin", password="Merlin007#",
            #               host="wayrem.c08qmktlafbu.us-east-1.rds.amazonaws.com", database="wayrem_8.2")

            df_ingredients = pd.read_sql(
                'select * from ingredient_master', con)
            df = pd.read_excel(file)
            # df.columns = df.iloc[0]
            # df = df.drop(0)
            df = df[df.columns.dropna()]
            df = df.fillna(0)
            df3 = df.merge(df_ingredients, how='outer',
                           indicator=True).loc[lambda x: x['_merge'] == 'left_only']

            ids = []
            uuids = []

            for id_counter in range(0, len(df3.index)):
                ids.append(str(uuid.uuid4()))
                df3['ingredients_status'] = 'Active'
            for i in ids:
                uuids.append((uuid.UUID(i)).hex)
            df3['id'] = uuids
            df3['created_at'] = datetime.now()
            df3['updated_at'] = datetime.now()
            df3 = df3.drop('_merge', axis=1)

            df3.to_sql('ingredient_master', engine,
                       if_exists='append', index=False)
            messages.success(request, "Ingredients imported successfully!")
            return redirect('wayrem_admin:ingredientslist')
        except:
            messages.error(request, "Please select a valid file!")
    return redirect('wayrem_admin:ingredientslist')
