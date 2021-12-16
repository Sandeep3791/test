from django.urls import path
from wayrem_admin import views

urlpatterns = [
    path('excel_subcategory/', views.subcategories_excel, name='excelsubcategory'),
    path('createsubcategory/', views.create_subcategory, name='createsubcategory'),
    path('subcategories-list/', views.SubCategoriesList.as_view(),
         name='subcategorieslist'),
    path('delete-subcategories/', views.DeleteSubCategories.as_view(),
         name='deletesubcategories'),
    path('update-subcategories/<str:id>/',
         views.update_subcategories, name='updatesubcategory'),
    path('category-details/<str:id>/',
         views.subcategory_details, name='categoriesdetails'),

]
