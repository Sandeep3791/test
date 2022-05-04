from django.db.models import Q
from wayrem_admin.permissions.models import FunctionMaster
from wayrem_admin.users.backends import MyAuthBackend
from wayrem_admin.users.models import Users
from django.contrib.auth.decorators import login_required
from django.template.defaultfilters import join
from django.conf import settings

def show_menu(request):
    """
    Return a menu along with user permission set'.
    """
    if request.is_ajax():
        return {'pages_menu': {}}    
    if not request.user.is_authenticated:
        return {'pages_menu': {}}
    pages_menu_list = []
    pages_menu_dict = {}
    
    menu_temp_dict = {}
    sub_list = []
    backend = MyAuthBackend()
    permissions = backend.get_user_permissions(request.user)
    #print("permissions==",permissions)
    if request.user.is_superuser != 1:
        pages_menu = FunctionMaster.objects.filter(Q(status='1') & Q(show_in_menu='yes') & Q(codename__in=permissions)).order_by('display_order')
        parent_id_list = []
        if pages_menu:
            for menu in pages_menu:
                if menu.parent_id > 0:
                    parent_id_list.append(menu.parent_id)
        if parent_id_list:
            pages_menu = FunctionMaster.objects.filter(Q(status='1') & Q(show_in_menu='yes') & Q(codename__in=permissions) | Q(id__in=parent_id_list)).order_by('display_order')
        
    else:       
        pages_menu = FunctionMaster.objects.filter(Q(status='1') & Q(show_in_menu='yes')).order_by('display_order') 
    #print(pages_menu.query)
    if pages_menu:       
        for menu in pages_menu:                          
            if menu.parent_id == 0:                
                pages_menu_list.append(menu.id)                
                menu_temp_dict[menu.id] = menu.__dict__
                                                 
        for function_id in pages_menu_list: 
            menu_dict = {}           
            menu_dict['menu'] = menu_temp_dict[function_id] 
            for menu in pages_menu:
                if menu.parent_id == function_id:
                    sub_list.append(menu.__dict__)               
            if sub_list: 
                menu_dict['submenu']  = sub_list.copy()                
            pages_menu_dict[function_id] = menu_dict
            sub_list.clear()
    require_https=request.is_secure()
    # print(pages_menu_dict)    
    if not request.is_ajax():
        current_path = request.path.strip('/') 
        #print(search(pages_menu_dict, current_path)
    
    return {'pages_menu': pages_menu_dict,'require_https':settings.FLAG_SSL}

def search(myDict, lookup):
    for p_key, prent_dict in myDict.items():
        for menu_items in prent_dict:
            print(menu_items['action_path'])
            
def common_constants(request):
    CS_MODULE_ID = 3        
    module_id = get_module_id(request)
    constants_dict = {}
    return constants_dict

def get_module_id(request):
    module_id = 0
    if not request.is_ajax():
        action_path = request.get_full_path().rstrip('/')
        try:
            module_list = FunctionMaster.objects.filter(Q(action_path=action_path)).all()[0:1].values('module_id')
            module_id = module_list[0]['module_id']
        except:
            module_id = 0
    return module_id
        
