from rolepermissions.roles import AbstractUserRole


class DNDSTech(AbstractUserRole):
    available_permissions = {
        'create_user': True,
    }


class Guest(AbstractUserRole):
    available_permissions = {
        'can_vew': True,
    }


class Partner(AbstractUserRole):
    available_permissions = {
        'create_medical_record': True,
    }


class DeskAdmin(AbstractUserRole):
    available_permissions = {
        'create_medical_record': True,
    }


class DeskAssistantAdmin(AbstractUserRole):
    available_permissions = {
        'create_medical_record': True,
    }
