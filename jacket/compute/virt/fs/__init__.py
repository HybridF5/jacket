__author__ = 'Administrator'


import eventlet
from oslo_config import cfg
from oslo_log import log as logging
from oslo_utils import importutils

from novaclient import client as novaclient
from novaclient import shell as novashell
from jacket.compute import exception
from jacket import context
#from jacket.compute.openstack.common import local
from glanceclient.v2 import client as glanceclient
from keystoneclient.v2_0 import client as kc
from keystoneclient.v3 import client as kc_v3
from cinderclient import client as cinderclient


logger = logging.getLogger(__name__)

class ClientsManager(object):
    def __init__(self, context):
        """
        :param context type RequestContext, nova.openstack.common.context.RequestContext
        """
        self._keystone = None
        self._cinder = None
        self.context = context

    @property
    def auth_token(self):
        # if there is no auth token in the context
        # attempt to get one using the context username and password
        return self.context.auth_token or self.keystone().auth_token

    def url_for(self, **kwargs):
        return self.keystone().url_for(**kwargs)

    def keystone(self):
        if self._keystone:
            return self._keystone

        self._keystone = KeystoneClient(self.context)
        return self._keystone

    def nova(self):
        con = self.context
        if self.auth_token is None:
            logger.error("Nova connection failed, no auth_token!")
            return None

        computeshell = novashell.OpenStackComputeShell()
        extensions = novaclient.discover_extensions("1.1")

        args = {
            'project_id': con.tenant,
            'auth_url': con.auth_url,
            'service_type': 'compute',
            'username': con.username,
            'insecure': True,
            'api_key': con.password,
            'region_name': con.region_name,
            'extensions': extensions,
            'timeout': 180
        }
        if con.password is not None:
            if self.context.region_name is None:
                management_url = self.url_for(service_type='compute')
            else:
                management_url = self.url_for(
                    service_type='compute',
                    attr='region',
                    filter_value=self.context.region_name)
        else:
            management_url = con.nova_url + '/' + con.tenant_id
        client = novaclient.Client(2, **args)
        client.client.auth_token = self.auth_token
        client.client.management_url = management_url

        return client

    def glance(self):
        con = self.context
        if self.auth_token is None:
            logger.error("Nova connection failed, no auth_token!")
            return None
        glance_endpoint = self.url_for(service_type='image', endpoint_type='publicURL')
        client = glanceclient.Client(glance_endpoint, token=self.auth_token, insecure=True)

        return client

    def cinder(self):
        if self._cinder:
            return self._cinder

        con = self.context
        if self.auth_token is None:
            logger.error("Cinder connection failed, no auth_token!")
            return None

        args = {
            'service_type': 'volume',
            'auth_url': con.auth_url,
            'project_id': con.tenant,
            'insecure': True,
            'username': con.username,
            'api_key': con.password,
            'timeout': 180
        }

        self._cinder = cinderclient.Client('1', **args)
        if con.password is not None:
            if self.context.region_name is None:
                management_url = self.url_for(service_type='volume')
            else:
                management_url = self.url_for(
                    service_type='volume',
                    attr='region',
                    filter_value=self.context.region_name)
        else:
            management_url = con.cinder_url % {'project_id':con.tenant_id}
        self._cinder.client.auth_token = self.auth_token
        self._cinder.client.management_url = management_url

        return self._cinder


class KeystoneClient(object):

    """
    Wrap keystone client so we can encapsulate logic used in resources
    Note this is intended to be initialized from a resource on a per-session
    basis, so the session context is passed in on initialization
    Also note that a copy of this is created every resource as self.keystone()
    via the code in engine/client.py, so there should not be any need to
    directly instantiate instances of this class inside resources themselves
    """

    def __init__(self, context):
        # We have to maintain two clients authenticated with keystone:
        # - ec2 interface is v2.0 only
        # - trusts is v3 only
        # If a trust_id is specified in the context, we immediately
        # authenticate so we can populate the context with a trust token
        # otherwise, we delay client authentication until needed to avoid
        # unnecessary calls to keystone.
        #
        # Note that when you obtain a token using a trust, it cannot be
        # used to reauthenticate and get another token, so we have to
        # get a new trust-token even if context.auth_token is set.
        #
        # - context.auth_url is expected to contain the v2.0 keystone endpoint
        self.context = context
        self._client_v2 = None
        self._client_v3 = None

        if self.context.trust_id:
            # Create a connection to the v2 API, with the trust_id, this
            # populates self.context.auth_token with a trust-scoped token
            self._client_v2 = self._v2_client_init()

    @property
    def client_v3(self):
        if not self._client_v3:
            # Create connection to v3 API
            self._client_v3 = self._v3_client_init()
        return self._client_v3

    @property
    def client_v2(self):
        if not self._client_v2:
            self._client_v2 = self._v2_client_init()
        return self._client_v2

    def _v2_client_init(self):
        kwargs = {
            'auth_url': self.context.auth_url,
            'insecure': True,
        }
        auth_kwargs = {}
        # Note try trust_id first, as we can't reuse auth_token in that case
        if self.context.trust_id is not None:
            # We got a trust_id, so we use the admin credentials
            # to authenticate, then re-scope the token to the
            # trust impersonating the trustor user.
            # Note that this currently requires the trustor tenant_id
            # to be passed to the authenticate(), unlike the v3 call
            kwargs.update(self._service_admin_creds(api_version=2))
            auth_kwargs['trust_id'] = self.context.trust_id
            auth_kwargs['tenant_id'] = self.context.tenant_id
        elif self.context.auth_token is not None:
            kwargs['tenant_name'] = self.context.tenant
            kwargs['token'] = self.context.auth_token
        elif self.context.password is not None:
            kwargs['username'] = self.context.username
            kwargs['password'] = self.context.password
            kwargs['tenant_name'] = self.context.tenant
            kwargs['tenant_id'] = self.context.tenant_id
        else:
            logger.error("Keystone v2 API connection failed, no password or "
                         "auth_token!")
            raise exception.AuthorizationFailure()

        client_v2 = kc.Client(**kwargs)

        client_v2.authenticate(**auth_kwargs)
        # If we are authenticating with a trust auth_kwargs are set, so set
        # the context auth_token with the re-scoped trust token
        if auth_kwargs:
            # Sanity check
            if not client_v2.auth_ref.trust_scoped:
                logger.error("v2 trust token re-scoping failed!")
                raise exception.AuthorizationFailure()
            # All OK so update the context with the token
            self.context.auth_token = client_v2.auth_ref.auth_token
            self.context.auth_url = kwargs.get('auth_url')

        return client_v2

    @staticmethod
    def _service_admin_creds(api_version=2):
        # Import auth_token to have keystone_authtoken settings setup.
        importutils.import_module('keystoneclient.middleware.auth_token')

        creds = {
            'username': cfg.CONF.keystone_authtoken.admin_user,
            'password': cfg.CONF.keystone_authtoken.admin_password,
        }
        if api_version >= 3:
            creds['auth_url'] =\
                cfg.CONF.keystone_authtoken.auth_uri.replace('v2.0', 'v3')
            creds['project_name'] =\
                cfg.CONF.keystone_authtoken.admin_tenant_name
        else:
            creds['auth_url'] = cfg.CONF.keystone_authtoken.auth_uri
            creds['tenant_name'] =\
                cfg.CONF.keystone_authtoken.admin_tenant_name

        return creds

    def _v3_client_init(self):
        kwargs = {}
        if self.context.auth_token is not None:
            kwargs['project_name'] = self.context.tenant
            kwargs['token'] = self.context.auth_token
            kwargs['auth_url'] = self.context.auth_url.replace('v2.0', 'v3')
            kwargs['endpoint'] = kwargs['auth_url']
        elif self.context.trust_id is not None:
            # We got a trust_id, so we use the admin credentials and get a
            # Token back impersonating the trustor user
            kwargs.update(self._service_admin_creds(api_version=3))
            kwargs['trust_id'] = self.context.trust_id
        elif self.context.password is not None:
            kwargs['username'] = self.context.username
            kwargs['password'] = self.context.password
            kwargs['project_name'] = self.context.tenant
            kwargs['project_id'] = self.context.tenant_id
            kwargs['auth_url'] = self.context.auth_url.replace('v2.0', 'v3')
            kwargs['endpoint'] = kwargs['auth_url']
        else:
            logger.error("Keystone v3 API connection failed, no password or "
                         "auth_token!")
            raise exception.AuthorizationFailure()

        client = kc_v3.Client(**kwargs)
        # Have to explicitly authenticate() or client.auth_ref is None
        client.authenticate()

        return client

    def create_trust_context(self):
        """
        If cfg.CONF.deferred_auth_method is trusts, we create a
        trust using the trustor identity in the current context, with the
        trustee as the heat service user and return a context containing
        the new trust_id

        If deferred_auth_method != trusts, or the current context already
        contains a trust_id, we do nothing and return the current context
        """
        if self.context.trust_id:
            return self.context

        # We need the service admin user ID (not name), as the trustor user
        # can't lookup the ID in keystoneclient unless they're admin
        # workaround this by creating a temporary admin client connection
        # then getting the user ID from the auth_ref
        admin_creds = self._service_admin_creds()
        admin_client = kc.Client(**admin_creds)
        trustee_user_id = admin_client.auth_ref.user_id
        trustor_user_id = self.client_v3.auth_ref.user_id
        trustor_project_id = self.client_v3.auth_ref.project_id
        roles = cfg.CONF.trusts_delegated_roles
        trust = self.client_v3.trusts.create(trustor_user=trustor_user_id,
                                             trustee_user=trustee_user_id,
                                             project=trustor_project_id,
                                             impersonation=True,
                                             role_names=roles)

        trust_context = context.RequestContext.from_dict(
            self.context.to_dict())
        trust_context.trust_id = trust.id
        trust_context.trustor_user_id = trustor_user_id
        return trust_context

    def delete_trust(self, trust_id):
        """
        Delete the specified trust.
        """
        self.client_v3.trusts.delete(trust_id)

    def create_stack_user(self, username, password=''):
        """
        Create a user defined as part of a stack, either via template
        or created internally by a resource.  This user will be added to
        the heat_stack_user_role as defined in the config
        Returns the keystone ID of the resulting user
        """
        if(len(username) > 64):
            logger.warning("Truncating the username %s to the last 64 "
                           "characters." % username)
            # get the last 64 characters of the username
            username = username[-64:]
        user = self.client_v2.users.create(username,
                                           password,
                                           '%s@heat-api.org' %
                                           username,
                                           tenant_id=self.context.tenant_id,
                                           enabled=True)

        # We add the new user to a special keystone role
        # This role is designed to allow easier differentiation of the
        # heat-generated "stack users" which will generally have credentials
        # deployed on an instance (hence are implicitly untrusted)
        roles = self.client_v2.roles.list()
        stack_user_role = [r.id for r in roles
                           if r.name == cfg.CONF.heat_stack_user_role]
        if len(stack_user_role) == 1:
            role_id = stack_user_role[0]
            logger.debug("Adding user %s to role %s" % (user.id, role_id))
            self.client_v2.roles.add_user_role(user.id, role_id,
                                               self.context.tenant_id)
        else:
            logger.error("Failed to add user %s to role %s, check role exists!"
                         % (username, cfg.CONF.heat_stack_user_role))

        return user.id

    def delete_stack_user(self, user_id):

        user = self.client_v2.users.get(user_id)

        # FIXME (shardy) : need to test, do we still need this retry logic?
        # Copied from user.py, but seems like something we really shouldn't
        # need to do, no bug reference in the original comment (below)...
        # tempory hack to work around an openstack bug.
        # seems you can't delete a user first time - you have to try
        # a couple of times - go figure!
        tmo = eventlet.Timeout(10)
        status = 'WAITING'
        reason = 'Timed out trying to delete user'
        try:
            while status == 'WAITING':
                try:
                    user.delete()
                    status = 'DELETED'
                except Exception as ce:
                    reason = str(ce)
                    logger.warning("Problem deleting user %s: %s" %
                                   (user_id, reason))
                    eventlet.sleep(1)
        except eventlet.Timeout as t:
            if t is not tmo:
                # not my timeout
                raise
            else:
                status = 'TIMEDOUT'
        finally:
            tmo.cancel()

        if status != 'DELETED':
            raise exception.Error(reason)

    def delete_ec2_keypair(self, user_id, accesskey):
        self.client_v2.ec2.delete(user_id, accesskey)

    def get_ec2_keypair(self, user_id):
        # We make the assumption that each user will only have one
        # ec2 keypair, it's not clear if AWS allow multiple AccessKey resources
        # to be associated with a single User resource, but for simplicity
        # we assume that here for now
        cred = self.client_v2.ec2.list(user_id)
        if len(cred) == 0:
            return self.client_v2.ec2.create(user_id, self.context.tenant_id)
        if len(cred) == 1:
            return cred[0]
        else:
            logger.error("Unexpected number of ec2 credentials %s for %s" %
                         (len(cred), user_id))

    def disable_stack_user(self, user_id):
        # FIXME : This won't work with the v3 keystone API
        self.client_v2.users.update_enabled(user_id, False)

    def enable_stack_user(self, user_id):
        # FIXME : This won't work with the v3 keystone API
        self.client_v2.users.update_enabled(user_id, True)

    def url_for(self, **kwargs):
        return self.client_v2.service_catalog.url_for(**kwargs)

    @property
    def auth_token(self):
        return self.client_v2.auth_token


class Clients(object):

    def __init__(self, user=None, pwd=None, auth_url=None, tenant=None, region=None):
        self._init_user_info(user, pwd, auth_url, tenant, region)
        clients = ClientsManager(self._get_context())
        self.keystone_client = clients.keystone().client_v2
        self.novaclient = clients.nova()
        self.glanceclient = clients.glance()
        self.cinderclient = clients.cinder()

    def _init_user_info(self, user, pwd, auth_url, tenant, region):
        if user:
            self.USER = user
        else:
            self.USER = 'cloud_admin'

        if pwd:
            self.PWD = pwd
        else:
            self.PWD = 'FusionSphere123'

        if auth_url:
            self.OS_AUTH_URL = auth_url
        else:
            self.OS_AUTH_URL = 'https://identity.az01.sz--fusionsphere.huawei.com:443/identity/v2.0'

        if tenant:
            self.TENANT = tenant
        else:
            self.TENANT = 'admin'

        if region:
            self.REGION = region
        else:
            self.REGION = 'az01.sz--fusionsphere'

    def _get_keystone_credentials(self):
        d = {}
        d['version'] = '2'
        d['username'] = self.USER
        d['password'] = self.PWD
        d['auth_url'] = self.OS_AUTH_URL
        d['project_id'] = self.TENANT
        d['tenant'] = self.TENANT
        if self.REGION is not None:
            d['region_name'] = self.REGION

        return d

    def _get_context(self):
        credentials = self._get_keystone_credentials()
        sub_fs_context = RequestContext(**credentials)
        return sub_fs_context


class RequestContext(context.RequestContext):

    """
    Stores information about the security context under which the user
    accesses the system, as well as additional request information.
    """

    def __init__(self, auth_token=None, username=None, password=None,
                 aws_creds=None, tenant=None,
                 tenant_id=None, auth_url=None, roles=None,
                 is_admin=False, region_name=None,
                 nova_url=None, cinder_url=None, neutron_url=None,
                 read_only=False, show_deleted=False,
                 owner_is_tenant=True, overwrite=True,
                 trust_id=None, trustor_user_id=None,
                 **kwargs):
        """
        :param overwrite: Set to False to ensure that the greenthread local
            copy of the index is not overwritten.

         :param kwargs: Extra arguments that might be present, but we ignore
            because they possibly came in from older rpc messages.
        """
        super(RequestContext, self).__init__(auth_token=auth_token,
                                             user=username, tenant=tenant,
                                             is_admin=is_admin,
                                             read_only=read_only,
                                             show_deleted=show_deleted,
                                             request_id='unused')
        self.username = username
        self.password = password
        self.aws_creds = aws_creds
        self.tenant_id = tenant_id
        self.auth_url = auth_url
        self.roles = roles or []
        self.owner_is_tenant = owner_is_tenant
        # if overwrite or not hasattr(local.store, 'context'):
        #    self.update_store()
        self._session = None
        self.trust_id = trust_id
        self.trustor_user_id = trustor_user_id
        self.nova_url = nova_url
        self.cinder_url = cinder_url
        self.neutron_url = neutron_url
        self.region_name = region_name

    # def update_store(self):
    #    local.store.context = self

    def to_dict(self):
        return {'auth_token': self.auth_token,
                'username': self.username,
                'password': self.password,
                'aws_creds': self.aws_creds,
                'tenant': self.tenant,
                'tenant_id': self.tenant_id,
                'trust_id': self.trust_id,
                'trustor_user_id': self.trustor_user_id,
                'auth_url': self.auth_url,
                'roles': self.roles,
                'is_admin': self.is_admin}

    @classmethod
    def from_dict(cls, values):
        return cls(**values)

    @property
    def owner(self):
        """Return the owner to correlate with an image."""
        return self.tenant if self.owner_is_tenant else self.user


if __name__ == '__main__':
    clients = Clients()
    glance_client = clients.glanceclient

    s = glance_client.images.list(filters={'name':'image@dd2a5a9f-5c44-4849-91b7-e1861c309ee0'})
    image_list = list(s)
    print image_list

    if image_list and len(image_list) > 0:
        d_image = glance_client.images.get(image_list[0].id)
        print d_image
