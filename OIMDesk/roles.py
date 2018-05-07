from rolepermissions.roles import AbstractUserRole


class DNDSTech(AbstractUserRole):
    available_permissions = {
        'create_superuseruser': True,
        'create_admin_user': True,
        'create_assistant_user': True,
        'create_controle_user': True,
        'create_user': True,
        'create_export_xls': True,
        'create_edite_data': True,
    }


class DeskAdmin(AbstractUserRole):
    available_permissions = {
        # 'controle_data': True,
        'create_assistant_user': True,
        'create_controle_user': True,
        'create_user': True,
        'create_export_xls': True,
        'create_edite_data': True,
    }


class DeskAssistantAdmin(AbstractUserRole):
    available_permissions = {
        'controle_data': True,
        'create_controle_user': True,
        'create_user': True,
        'create_export_xls': True,
        'create_edite_data': True,
    }


class DeskControle(AbstractUserRole):
    available_permissions = {
        'controle_data': True,
        'create_valide': True,
        'create_export_xls': True,
        'create_edite_data': True,
    }


class PartnerOIM(AbstractUserRole):
    available_permissions = {
        'can_vew': True,
        'can_send_message': True,
        'create_export_xls': True,
    }


class PartnerHCR(AbstractUserRole):
    available_permissions = {
        'can_vew': True,
        'can_send_message': True,
        'create_export_xls': True,
    }


class Guest(AbstractUserRole):
    available_permissions = {
        'can_vew': True,
    }
