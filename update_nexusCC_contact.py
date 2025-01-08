from Utils.cod_post import cod_post, cod_session_end, cod_session_start
from Utils.cod_get import cod_get
from Utils.logger import log_info
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
from os import environ

#Importing Environment Variables
load_dotenv()
LOGPATH = environ.get('LOGPATH')



#Setting Up Logger
def message(string, sys_name):
    print(string)
    log_info(string, sys_name, LOGPATH)


#Get System Name
def get_system_name(ip, cookie):
    res_xml = cod_get(ip, 'Configuration/SystemUnit/Name', cookie)
    print(res_xml)
    res_root = ET.fromstring(res_xml)
    sys_name = res_root.find(".//SystemUnit/Name").text
    return sys_name
    

#Check if contact exists
def check_contact(ip, cookie):
    search_XML = f'''<Command>
    <Phonebook>
        <Search>
            <SearchField>Name</SearchField>
            <SearchString>Nexus CC</SearchString>
        </Search>
    </Phonebook>
    </Command>'''
    res_XML = cod_post(ip, search_XML, cookie)
    res_root = ET.fromstring(res_XML)
    rows = res_root.find(".//*ResultInfo/TotalRows").text
    print(rows)

    res_dict = {
        'contact_found': False,
        'contact_id': '',
        'contact_method_id': '',
        'number': ''
    }
    #If contact exists, return contact ID
    if rows == '1':
        contact_id = res_root.find(".//*Contact/ContactId").text
        contact_method_id = res_root.find(".//*ContactMethodId").text
        number = res_root.find(".//*ContactMethod/Number").text
        res_dict['contact_found'] = True
        res_dict['contact_id'] = contact_id
        res_dict['contact_method_id'] = contact_method_id
        res_dict['number'] = number
        return res_dict
    else:
        return res_dict

#If contact exists, modify contact using contact ID
def modify_contact(ip, cookie, contact_id, contact_method_id):
    modify_XML = f'''<Command>
            <Phonebook>
                <ContactMethod>
                    <Modify>
                        <ContactId>{contact_id}</ContactId>
                        <ContactMethodId>{contact_method_id}</ContactMethodId>
                        <Number>placeholder.mskcc@m.webex.com</Number>
                    </Modify>
                </ContactMethod>
            </Phonebook>
        </Command>'''
    
    response = cod_post(ip, modify_XML, cookie)
    return response

#If contact does not exist, create contact
def create_contact(ip, cookie):
    create_XML = f'''<Command>
            <Phonebook>
                <Contact>
                    <Add>
                        <Name>Nexus CC</Name>
                        <Number>placeholder.mskcc@m.webex.com</Number>
                        <Tag>Favorite</Tag>
                    </Add>
                </Contact>
            </Phonebook>
        </Command>'''
    
    response = cod_post(ip, create_XML, cookie)
    return response

#Main Function Name
def update_nexusCC_contact(ip):
    sesh_cookie = cod_session_start(ip)
    new_number = 'NewPlaceholder.mskcc@m.webex.com'
    try:
        sys_name = get_system_name(ip, sesh_cookie)
        message(f'Got system name: {sys_name}', ip)
        message(f'Checking for Command Center contact on {sys_name}', sys_name)
        contact_dict = check_contact(ip, sesh_cookie)
        if contact_dict['contact_found'] == True:
            message(f'Contact found on {sys_name}.', sys_name)
            if contact_dict['number'] != new_number:
                modify_contact(ip, sesh_cookie, contact_dict['contact_id'], contact_dict['contact_method_id'])
                message(f'Contact successfully updated on {sys_name}. Exiting', sys_name)
                cod_session_end(ip, sesh_cookie)
                return (f'Contact successfully updated on {sys_name}')
            else:
                message(f'Contact dial number is current on {sys_name}. Exiting', sys_name)
                cod_session_end(ip, sesh_cookie)
                return f'Contact dial number is current on {sys_name}. Exiting'
        else:
            message(f'Contact not found on {sys_name}. Creating contact', sys_name)
            create_contact(ip, sesh_cookie)
            message(f'Contact successfully created on {sys_name}. Exiting.', sys_name)
            cod_session_end(ip, sesh_cookie)
            return(f'Contact successfully created on {sys_name}')

    except Exception as err:
        message(err, sys_name)
        cod_session_end(ip, sesh_cookie)
        return err

if __name__ == '__main__':
    ip = '172.16.131.163'
    update_nexusCC_contact(input('Codec IP: '))
    # sesh_cookie = cod_session_start(ip)
    # name = get_system_name(ip, sesh_cookie)
    # print(name)
