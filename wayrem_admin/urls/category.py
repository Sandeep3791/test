from django.urls import path
from wayrem_admin import views

urlpatterns = [
    path('excel_category/', views.categories_excel, name='excelcategory'),
    path('pdf_category/', views.pdf_category, name='categorypdf'),
    path('createcategory/', views.create_category, name='createcategory'),
    path('categories-list/', views.CategoriesList.as_view(), name='categorieslist'),
    path('delete-categories/', views.DeleteCategories.as_view(),
         name='deletecategories'),
    path('update-categories/<str:id>/',
         views.update_categories, name='updatecategory'),

]
