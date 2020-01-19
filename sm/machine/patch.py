patch_conf = { 'patched': False}
#patched = False


if patch_conf['patched'] is False:
    from gevent import monkey; monkey.patch_all()
    from huey import SqliteHuey

    from machine import django_connect
    django_connect.safe_bind()

    patch_conf['patched'] = True
