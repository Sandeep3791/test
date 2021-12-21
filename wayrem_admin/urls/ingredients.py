from django.urls import path
from wayrem_admin import views

urlpatterns = [
    path('excel_ingredient/', views.ingredient_excel, name='excelingredient'),
    path('create-ingredients/', views.create_ingredients, name='createingredients'),
    path('ingredients-list/', views.ingredientsList, name='ingredientslist'),
    path('delete-ingredients/', views.DeleteIngredients.as_view(),
         name='deleteingredients'),
    path('update-ingredients/<str:id>/',
         views.update_ingredients, name='updateingredients'),
    path('import-ingredients/', views.import_ingredients, name="importingredients"),

]
