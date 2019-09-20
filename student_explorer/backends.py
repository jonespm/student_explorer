from djangosaml2.backends import Saml2Backend
from django.core.exceptions import PermissionDenied
from django.conf import settings

import logging

logger = logging.getLogger(__name__)


class ActiveUserOnlySAML2Backend(Saml2Backend):
    def authenticate(self, **kwargs):
        user = None
        try:
            user = super(ActiveUserOnlySAML2Backend, self).authenticate(**kwargs)
        except PermissionDenied:
            # If user 
            if user:
                user.is_active = False
                user.save()
            raise PermissionDenied
        # If the user doesn't exist for some reason return permission denied
        if not user:
            raise PermissionDenied
        # The user should be made active if they exist and aren't active
        if not user.is_active:
           user.is_active = True
           user.save()
        return user
            

    def is_authorized(self, attributes, attribute_mapping):
        # If there are any groups that we're a member of, return true
        if attributes.get('isMemberOf'):
            logger.debug(attributes.get('isMemberOf'))
            return True
        else:
            logger.warn('The user "%s" is not in one of the allowed groups', attributes.get('uid'))
            raise PermissionDenied
