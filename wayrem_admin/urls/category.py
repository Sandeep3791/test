from django.urls import path
from wayrem_admin import views

urlpatterns = [
    path('excel_category/', views.categories_excel, name='excelcategory'),
    path('addcategory/', views.add_category, name='addcategory'),
    path('categories-list/', views.CategoriesList.as_view(), name='categorieslist'),
    path('delete-categories/', views.DeleteCategories.as_view(),
         name='deletecategories'),
    path('update-categories/<str:id>/',
         views.update_categories, name='updatecategory'),
    path('category-details/<str:id>/',
         views.category_details, name='categorydetails'),
    path('delete-categories/', views.DeleteCategories.as_view(),
         name='deletecategories'),

]
